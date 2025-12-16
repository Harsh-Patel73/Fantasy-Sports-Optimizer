"""
The Odds API data fetcher.

Fetches real-time odds from 50+ sportsbooks via The Odds API.
Supports NFL, NBA, MLB, NHL with both game lines and player props.
"""
import requests
from datetime import datetime
from decimal import Decimal
from config import get_config
from app.db import get_session
from app.models import Books, Statlines, Matchups, Props
from app.utils import normalize_stat_type

# Configuration
config = get_config()
API_KEY = config.ODDS_API_KEY
BASE_URL = config.ODDS_API_BASE_URL
REGIONS = config.ODDS_API_REGIONS
ODDS_FORMAT = config.ODDS_API_ODDS_FORMAT

# Sports to fetch
SPORTS = {
    'americanfootball_nfl': 'NFL',
    'basketball_nba': 'NBA',
    'baseball_mlb': 'MLB',
    'icehockey_nhl': 'NHL',
}

# Game market types
GAME_MARKETS = ['h2h', 'spreads', 'totals']

# Player prop markets by sport
PLAYER_PROP_MARKETS = {
    'americanfootball_nfl': [
        'player_pass_yds', 'player_pass_tds', 'player_rush_yds',
        'player_reception_yds', 'player_receptions', 'player_anytime_td',
    ],
    'basketball_nba': [
        'player_points', 'player_rebounds', 'player_assists',
        'player_threes', 'player_points_rebounds_assists',
        'player_points_rebounds', 'player_points_assists',
        'player_rebounds_assists', 'player_steals', 'player_blocks',
    ],
    'baseball_mlb': [
        'batter_home_runs', 'batter_hits', 'batter_total_bases',
        'batter_rbis', 'pitcher_strikeouts',
    ],
    'icehockey_nhl': [
        'player_goals', 'player_assists', 'player_points',
        'player_shots_on_goal', 'player_power_play_points',
    ],
}


class OddsAPIClient:
    """Client for The Odds API with quota tracking."""

    def __init__(self):
        self.requests_remaining = None
        self.requests_used = None

    def _make_request(self, endpoint, params=None):
        """Make API request and track quota."""
        if params is None:
            params = {}
        params['apiKey'] = API_KEY

        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)

        # Track quota from headers
        self.requests_remaining = response.headers.get('x-requests-remaining')
        self.requests_used = response.headers.get('x-requests-used')

        if self.requests_remaining:
            print(f"  [API Quota] Remaining: {self.requests_remaining}, Used: {self.requests_used}")

        response.raise_for_status()
        return response.json()

    def get_sports(self):
        """Get list of available sports."""
        return self._make_request('sports')

    def get_odds(self, sport, markets='h2h', regions=REGIONS):
        """Get odds for a sport's games."""
        params = {
            'regions': regions,
            'markets': markets,
            'oddsFormat': ODDS_FORMAT,
        }
        return self._make_request(f'sports/{sport}/odds', params)

    def get_events(self, sport):
        """Get list of events for a sport."""
        return self._make_request(f'sports/{sport}/events')

    def get_event_odds(self, sport, event_id, markets, regions=REGIONS):
        """Get odds for a specific event (used for player props)."""
        params = {
            'regions': regions,
            'markets': markets,
            'oddsFormat': ODDS_FORMAT,
        }
        return self._make_request(f'sports/{sport}/events/{event_id}/odds', params)


def get_or_create_book(session, book_name, book_type, timestamp):
    """Get existing book or create new one."""
    book = session.query(Books).filter_by(book_name=book_name).first()
    if not book:
        book = Books(book_name=book_name, book_type=book_type, scrape_timestamp=timestamp)
        session.add(book)
        session.flush()
    return book


def get_or_create_matchup(session, home_team, away_team, timestamp):
    """Get existing matchup or create new one."""
    matchup = session.query(Matchups).filter_by(
        home_team=home_team,
        away_team=away_team
    ).first()
    if not matchup:
        matchup = Matchups(
            home_team=home_team,
            away_team=away_team,
            scrape_timestamp=timestamp
        )
        session.add(matchup)
        session.flush()
    return matchup


def get_or_create_prop(session, category, units, description):
    """Get existing prop or create new one."""
    normalized_units = normalize_stat_type(units) if units else "Unknown"

    prop = session.query(Props).filter_by(
        category=category,
        units=normalized_units
    ).first()
    if not prop:
        prop = Props(
            category=category,
            units=normalized_units,
            description=description
        )
        session.add(prop)
        session.flush()
    return prop


def add_statline(session, book_id, player_name, matchup_id, prop_id, price, designation, points, line_type, timestamp):
    """Add a statline to the database."""
    statline = Statlines(
        book_id=book_id,
        player_name=player_name,
        matchup_id=matchup_id,
        prop_id=prop_id,
        price=Decimal(str(price)) if price is not None else None,
        designation=designation,
        points=Decimal(str(points)) if points is not None else Decimal('0.00'),
        line_type=line_type,
        scrape_timestamp=timestamp
    )
    session.add(statline)


def process_game_odds(session, odds_data, sport_name, market_type, timestamp, books_cache):
    """Process game odds (h2h, spreads, totals) and store in database."""
    count = 0

    for game in odds_data:
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')

        matchup = get_or_create_matchup(session, home_team, away_team, timestamp)

        # Determine category and stat type based on market
        category = "Game Lines"
        stat_type = normalize_stat_type(market_type)
        description = f"{sport_name} {stat_type}"

        prop = get_or_create_prop(session, category, stat_type, description)

        for bookmaker in game.get('bookmakers', []):
            book_name = bookmaker.get('title', 'Unknown')
            book_key = bookmaker.get('key', '')

            # Get or create book (with caching)
            if book_name not in books_cache:
                books_cache[book_name] = get_or_create_book(
                    session, book_name, "Sports Book", timestamp
                )
            book = books_cache[book_name]

            for market in bookmaker.get('markets', []):
                market_key = market.get('key', '')

                for outcome in market.get('outcomes', []):
                    team_name = outcome.get('name', '')
                    price = outcome.get('price')
                    point = outcome.get('point')

                    # Determine designation for totals
                    if market_key == 'totals':
                        designation = outcome.get('name', '').capitalize()  # Over/Under
                        player_name = f"{home_team} vs {away_team}"
                    else:
                        designation = None
                        player_name = team_name

                    add_statline(
                        session=session,
                        book_id=book.book_id,
                        player_name=player_name,
                        matchup_id=matchup.matchup_id,
                        prop_id=prop.prop_id,
                        price=price,
                        designation=designation,
                        points=point,
                        line_type=market_key,
                        timestamp=timestamp
                    )
                    count += 1

    return count


def process_player_props(session, event_odds, sport_name, matchup, timestamp, books_cache):
    """Process player prop odds and store in database."""
    count = 0

    for bookmaker in event_odds.get('bookmakers', []):
        book_name = bookmaker.get('title', 'Unknown')

        # Get or create book (with caching)
        if book_name not in books_cache:
            books_cache[book_name] = get_or_create_book(
                session, book_name, "Sports Book", timestamp
            )
        book = books_cache[book_name]

        for market in bookmaker.get('markets', []):
            market_key = market.get('key', '')
            stat_type = normalize_stat_type(market_key)

            prop = get_or_create_prop(
                session,
                "Player Props",
                stat_type,
                f"{sport_name} {stat_type}"
            )

            for outcome in market.get('outcomes', []):
                player_name = outcome.get('description', outcome.get('name', 'Unknown'))
                price = outcome.get('price')
                point = outcome.get('point')
                designation = outcome.get('name', '').capitalize()  # Over/Under

                add_statline(
                    session=session,
                    book_id=book.book_id,
                    player_name=player_name,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=price,
                    designation=designation,
                    points=point,
                    line_type=market_key,
                    timestamp=timestamp
                )
                count += 1

    return count


def fetch():
    """
    Fetch odds from The Odds API and store in database.

    This is the main entry point for the data fetcher.
    """
    if not API_KEY:
        print("ERROR: ODDS_API_KEY not configured. Please set it in .env file.")
        return

    print("\n" + "=" * 50)
    print("FETCHING DATA FROM THE ODDS API")
    print("=" * 50)

    client = OddsAPIClient()
    timestamp = datetime.now()
    Session = get_session()

    total_lines = 0
    books_cache = {}  # Cache books to avoid repeated queries

    with Session() as session:
        try:
            # Process each sport
            for sport_key, sport_name in SPORTS.items():
                print(f"\n--- {sport_name} ({sport_key}) ---")

                # Fetch game odds for each market type
                for market in GAME_MARKETS:
                    print(f"  Fetching {market} odds...")
                    try:
                        odds_data = client.get_odds(sport_key, markets=market)
                        count = process_game_odds(
                            session, odds_data, sport_name, market, timestamp, books_cache
                        )
                        total_lines += count
                        print(f"    Added {count} lines")
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 404:
                            print(f"    No {market} data available")
                        else:
                            print(f"    Error: {e}")
                    except Exception as e:
                        print(f"    Error fetching {market}: {e}")

                # Fetch player props (if available for this sport)
                if sport_key in PLAYER_PROP_MARKETS:
                    print(f"  Fetching player props...")
                    try:
                        events = client.get_events(sport_key)
                        prop_markets = ','.join(PLAYER_PROP_MARKETS[sport_key])

                        for event in events[:10]:  # Limit to conserve API quota
                            event_id = event.get('id')
                            home_team = event.get('home_team', 'Unknown')
                            away_team = event.get('away_team', 'Unknown')

                            matchup = get_or_create_matchup(
                                session, home_team, away_team, timestamp
                            )

                            try:
                                event_odds = client.get_event_odds(
                                    sport_key, event_id, prop_markets
                                )
                                count = process_player_props(
                                    session, event_odds, sport_name,
                                    matchup, timestamp, books_cache
                                )
                                total_lines += count
                                print(f"    {home_team} vs {away_team}: {count} prop lines")
                            except requests.exceptions.HTTPError as e:
                                if e.response.status_code == 404:
                                    print(f"    No props for {home_team} vs {away_team}")
                                else:
                                    print(f"    Error: {e}")
                            except Exception as e:
                                print(f"    Error fetching props: {e}")

                    except Exception as e:
                        print(f"    Error fetching events: {e}")

            session.commit()
            print(f"\n{'=' * 50}")
            print(f"FETCH COMPLETE: {total_lines} total lines from {len(books_cache)} sportsbooks")
            print(f"{'=' * 50}")

        except Exception as e:
            print(f"Database error: {e}")
            session.rollback()
            raise


# For backwards compatibility with main.py
def scrape():
    """Alias for fetch() to maintain compatibility."""
    fetch()
