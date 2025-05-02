import requests
import json

PINNACLE_API_URL = "https://www.pinnacle.com/config/app.json"

def combine_dicts(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            result.setdefault(key, []).append(value)
    return result

def pinnaclelines():
    try:
        response = requests.get(PINNACLE_API_URL)
        response.raise_for_status()
        api_config = response.json()
        API_KEY = api_config["api"]["haywire"]["apiKey"]
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
    j = 0

    try:
        matchups_url = "https://guest.api.arcadia.pinnacle.com/0.1/sports/4/matchups?withSpecials=true&brandId=0"
        print(f"Requesting matchups from: {matchups_url}")
        matchups_response = requests.get(matchups_url, headers=headers)
        matchups_response.raise_for_status()
        matchups = matchups_response.json()

        for matchup in matchups:
            if not matchup.get("isHighlighted", False):
                continue

            match_id = matchup.get("id")

            participants = matchup.get("participants", [])
            if len(participants) < 2:
                continue

            home_team = participants[0].get("name", "Unknown")
            away_team = participants[1].get("name", "Unknown")

            # Fetch related player info
            related_url = f"https://guest.api.arcadia.pinnacle.com/0.1/matchups/{match_id}/related"
            try:
                related_response = requests.get(related_url, headers=headers)
                related_response.raise_for_status()
                related_data = related_response.json()
            except Exception as e:
                print(f"Failed to fetch related data for {match_id}: {e}")
                continue

            # Map participantId to player name and units
            participant_lookup = {}
            for market in related_data if isinstance(related_data, list) else [related_data]:
                units = market.get("units", "Unknown Units")
                league_name = market['league']['name']
                sport_name = market['league']['sport']['name']
                for participant in market.get("participants", []):
                    pid = participant.get("id")
                    name = market.get("special", {}).get("description", participant.get("name", "Unknown Player"))
                    if pid:
                        participant_lookup[pid] = (name, units)

            # Fetch straight lines
            lines_url = f"https://guest.api.arcadia.pinnacle.com/0.1/matchups/{match_id}/markets/related/straight"
            try:
                lines_response = requests.get(lines_url, headers=headers)
                lines_response.raise_for_status()
                lines = lines_response.json()
            except Exception as e:
                print(f"Failed to fetch straight lines for {match_id}: {e}")
                continue

            for line in lines:
                prop_type = line.get('type')
                prices = line.get('prices', [])

                if len(prices) < 2:
                    continue

                player_id_home = prices[0].get('participantId')
                player_id_away = prices[1].get('participantId')

                player_name_home, units_home = participant_lookup.get(player_id_home, ("Unknown", ""))
                player_name_away, units_away = participant_lookup.get(player_id_away, ("Unknown", ""))

                prop_info[j] = {
                    "Prop Type": prop_type,
                    "Sport Name": sport_name,
                    "League Name": league_name,
                    "Player ID Home": player_id_home,
                    "Player Name Home": player_name_home,
                    "Units Home": units_home,
                    "Price Home": prices[0].get('price'),
                    "Points Home": prices[0].get('points'),
                    "Designation Home": prices[0].get('designation'),

                    "Player ID Away": player_id_away,
                    "Player Name Away": player_name_away,
                    "Units Away": units_away,
                    "Price Away": prices[1].get('price'),
                    "Points Away": prices[1].get('points'),
                    "Designation Away": prices[1].get('designation'),
                }

                game_odds_dict[j] = {
                    "Home Team": home_team,
                    "Away Team": away_team,
                }
                j += 1

    except requests.exceptions.RequestException as e:
        print("Error during API request:", e)
        return

    combined = combine_dicts(game_odds_dict, prop_info)


pinnaclelines()
