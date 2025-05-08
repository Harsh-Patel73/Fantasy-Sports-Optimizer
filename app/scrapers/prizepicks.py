import requests
from datetime import datetime
from decimal import Decimal
from app.db.session import SessionLocal
from app.models.books import Books
from app.models.statlines import Statlines
from app.models.matchups import Matchups
from app.models.props import Props

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'Referer': 'https://www.prizepicks.com/',
    'Origin': 'https://www.prizepicks.com',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

PROJECTIONS_URL = "https://api.prizepicks.com/projections?league_id=7&per_page=250&single_stat=true&in_game=true&state_code=TX&game_mode=pickem"

def get_or_create_matchup(session, home_team, away_team):
    matchup = session.query(Matchups).filter_by(home_team=home_team, away_team=away_team).first()
    if not matchup:
        matchup = Matchups(home_team=home_team, away_team=away_team, scrape_timestamp=datetime.now())
        session.add(matchup)
        session.flush()
    return matchup

def get_or_create_prop(session, category, units, description):
    if category == "total" and units is not None:
        category = "Player Props"

    prop = session.query(Props).filter_by(category=category, units=units).first()
    if not prop:
        prop = Props(category=category, units=units, description=description)
        session.add(prop)
        session.flush()

    return prop

def add_statline(session, book_id, player_name, matchup_id, prop_id, price, designation, points, line_type, timestamp):
    statline = Statlines(
        book_id=book_id,
        player_name=player_name,
        matchup_id=matchup_id,
        prop_id=prop_id,
        price=price,
        designation=designation,
        points=Decimal(points) if points is not None else Decimal('0.00'),
        line_type=line_type,
        scrape_timestamp=timestamp
    )
    session.add(statline)

def scrape():
    now = datetime.now()
    with SessionLocal() as session:
        try:
            book = Books(book_name="PrizePicks", book_type="Fantasy", scrape_timestamp=now)
            session.add(book)
            session.flush()

            response = requests.get(PROJECTIONS_URL, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            included_players = {
                item['id']: item['attributes']['name']
                for item in data.get('included', [])
                if item.get('type') == 'new_player'
            }

            for prop in data['data']:
                attr = prop['attributes']
                relationships = prop.get('relationships', {})
                player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                player_name = included_players.get(player_id)  # Will be None if not found

                units = attr.get("stat_display_name") or None
                category = "Player Props"
                points = attr.get("line_score")
                description = attr.get("description") or None
                line_type = attr.get("odds_type") or None

                # Normalize designation
                designation = "Over" if line_type in ("demon", "goblin") else None

                # Placeholder matchup (PrizePicks doesn’t expose real matchups)
                home_team = None
                away_team = None

                matchup = get_or_create_matchup(session, home_team, away_team)

                prop_entry = get_or_create_prop(
                    session,
                    category=category,
                    units=units,
                    description=f"{category} {units} Over/Under" if units else None
                )

                add_statline(
                    session=session,
                    book_id=book.book_id,
                    player_name=player_name,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop_entry.prop_id,
                    price=None,
                    designation=designation,
                    points=points,
                    line_type=line_type,
                    timestamp=now
                )

            session.commit()

        except Exception as e:
            print("Database error during export:", e)
            session.rollback()
