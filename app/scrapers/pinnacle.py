import requests
from datetime import datetime
from decimal import Decimal
from app.db import get_session
from app.models import Books, Statlines, Matchups, Props
from app.utils import normalize_stat_type

PINNACLE_API_URL = "https://www.pinnacle.com/config/app.json"


def combine_dicts(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            result.setdefault(key, []).append(value)
    return result

def get_or_create_matchup(session, home_team, away_team):
    matchup = session.query(Matchups).filter_by(home_team=home_team, away_team=away_team).first()
    if not matchup:
        matchup = Matchups(home_team=home_team, away_team=away_team, scrape_timestamp=datetime.now())
        session.add(matchup)
        session.flush()
    return matchup

def get_or_create_prop(session, category, units, description):
    normalized_units = normalize_stat_type(units)

    # If the category is 'total' and the units are not 'unknown', change the category to 'Player Props'
    if category == "total" and normalized_units != "unknown":
        category = "Player Props"

    # Now check if the prop already exists with the updated category
    prop = session.query(Props).filter_by(category=category, units=normalized_units, description=description).first()

    if not prop:
        prop = Props(category=category, units=normalized_units, description=description)
        session.add(prop)
        session.flush()
    return prop

def add_statline(session, book_id, player_name, matchup_id, prop_id, price, designation, points, prop_type, timestamp):
    statline = Statlines(
        book_id=book_id,
        player_name=player_name,
        matchup_id=matchup_id,
        prop_id=prop_id,
        price=price,
        designation=designation,
        points=Decimal(points) if points is not None else Decimal('0.00'),
        line_type=prop_type,
        scrape_timestamp=timestamp
    )
    session.add(statline)

def export_data(combined, game_odds_dict, prop_info):
    now = datetime.now()
    Session = get_session()
    with Session() as session:
        try:
            book = Books(book_name="Pinnacle", book_type="Sports Book", scrape_timestamp=now)
            session.add(book)
            session.flush()

            for game_id, _ in combined.items():
                matchup_data = game_odds_dict[game_id]
                prop = prop_info.get(game_id)

                if not prop:
                    continue

                home_team = matchup_data["Home Team"]
                away_team = matchup_data["Away Team"]
                player_full = prop.get("Player Name Home", "").split()
                player_name = " ".join(player_full[:2]) if player_full else "Unknown"
                units = prop.get("Units Home", "Unknown")
                prop_type = prop.get("Prop Type", "Unknown")
                description = f"{prop_type} Over/Under"
                normalized_units = normalize_stat_type(units)
                matchup = get_or_create_matchup(session, home_team, away_team)
                prop_entry = get_or_create_prop(session, prop_type, normalized_units, description)

                add_statline(session, book.book_id, player_name, matchup.matchup_id, prop_entry.prop_id,
                             prop.get("Price Home"), prop.get("Designation Home"),
                             prop.get("Points Home"), prop_type, now)

                add_statline(session, book.book_id, player_name, matchup.matchup_id, prop_entry.prop_id,
                             prop.get("Price Away"), prop.get("Designation Away"),
                             prop.get("Points Away"), prop_type, now)

            session.commit()
        except Exception as e:
            print("Database error during export:", e)
            session.rollback()

def scrape():
    try:
        config_response = requests.get(PINNACLE_API_URL)
        config_response.raise_for_status()
        API_KEY = config_response.json()["api"]["haywire"]["apiKey"]
    except Exception as e:
        print("Failed to fetch API key:", e)
        return

    headers = {
        "accept": "application/json",
        "origin": "https://www.pinnacle.com",
        "referer": "https://www.pinnacle.com/",
        "user-agent": "Mozilla/5.0",
        "x-api-key": API_KEY,
        "x-device-uuid": "a95be666-e4a9ef8e-d52b73dd-0d559878",
    }
    game_odds_dict = {}
    prop_info = {}
    index = 0

    try:
        matchups_url = "https://guest.api.arcadia.pinnacle.com/0.1/sports/4/matchups?withSpecials=true&brandId=0"
        matchups_response = requests.get(matchups_url, headers=headers)
        matchups_response.raise_for_status()

        for matchup in matchups_response.json():
            if not matchup.get("isHighlighted"):
                continue

            match_id = matchup.get("id")
            participants = matchup.get("participants", [])
            if len(participants) < 2:
                continue

            home_team = participants[0].get("name", "Unknown")
            away_team = participants[1].get("name", "Unknown")

            related_url = f"https://guest.api.arcadia.pinnacle.com/0.1/matchups/{match_id}/related"
            try:
                related_response = requests.get(related_url, headers=headers)
                related_response.raise_for_status()
                related_data = related_response.json()
            except Exception as e:
                print(f"Related fetch failed for {match_id}: {e}")
                continue

            participant_lookup = {}
            markets = related_data if isinstance(related_data, list) else [related_data]

            for market in markets:
                league_name = market.get('league', {}).get('name', '')
                sport_name = market.get('league', {}).get('sport', {}).get('name', '')
                units = market.get("units", "Unknown Units")
                for participant in market.get("participants", []):
                    pid = participant.get("id")
                    name = market.get("special", {}).get("description", participant.get("name", "Unknown"))
                    if pid:
                        participant_lookup[pid] = (name, units)

            lines_url = f"https://guest.api.arcadia.pinnacle.com/0.1/matchups/{match_id}/markets/related/straight"
            try:
                lines_response = requests.get(lines_url, headers=headers)
                lines_response.raise_for_status()
            except Exception as e:
                print(f"Straight lines fetch failed for {match_id}: {e}")
                continue

            for line in lines_response.json():
                prop_type = line.get('type', 'Unknown')
                prices = line.get('prices', [])
                if len(prices) < 2:
                    continue

                price0, price1 = prices[0], prices[1]
                pid_home, pid_away = price0.get('participantId'), price1.get('participantId')

                designation0 = price0.get("designation") or ("under" if price1.get("designation") == "over" else "over")
                designation1 = price1.get("designation") or ("under" if designation0 == "over" else "over")

                name_home, units_home = participant_lookup.get(pid_home, ("Unknown", ""))
                name_away, units_away = participant_lookup.get(pid_away, ("Unknown", ""))

                prop_info[index] = {
                    "Prop Type": prop_type,
                    "Sport Name": sport_name,
                    "League Name": league_name,
                    "Player ID Home": pid_home,
                    "Player Name Home": name_home,
                    "Units Home": units_home,
                    "Price Home": price0.get("price"),
                    "Points Home": price0.get("points"),
                    "Designation Home": designation0,
                    "Player ID Away": pid_away,
                    "Player Name Away": name_away,
                    "Units Away": units_away,
                    "Price Away": price1.get("price"),
                    "Points Away": price1.get("points"),
                    "Designation Away": designation1,
                }

                game_odds_dict[index] = {
                    "Home Team": home_team,
                    "Away Team": away_team,
                }
                index += 1

    except requests.RequestException as e:
        print("Error during API request:", e)
        return

    combined = combine_dicts(game_odds_dict, prop_info)
    export_data(combined, game_odds_dict, prop_info)