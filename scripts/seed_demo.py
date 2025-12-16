"""
Generate fake demo data for GitHub demo mode.

Uses fictional player names and team names to avoid licensing/ethical issues
with displaying scraped data publicly.

Usage:
    python scripts/seed_demo.py

This will create/overwrite the demo/demo.db SQLite database.
"""
import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add project root to path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set demo mode before importing app modules
os.environ['DEMO_MODE'] = 'true'

from app.db.session import get_engine, get_session
from app.models.base import Base
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props
from app.models.statlines import Statlines

# Fictional team names (not real NBA teams)
FAKE_TEAMS = [
    "Metro Wolves",
    "Harbor Eagles",
    "Summit Bears",
    "Valley Thunder",
    "Coast Sharks",
    "Mountain Lions",
    "River Hawks",
    "Desert Storm",
    "Forest Knights",
    "Urban Phoenix",
    "Northern Stars",
    "Southern Heat",
]

# Fictional player names
FAKE_PLAYERS = [
    "Marcus Johnson",
    "Tyler Williams",
    "Jordan Smith",
    "Alex Rodriguez",
    "Chris Thompson",
    "Michael Davis",
    "David Brown",
    "James Wilson",
    "Robert Miller",
    "Kevin Anderson",
    "Daniel Taylor",
    "Ryan Martinez",
    "Brandon Garcia",
    "Jason Lee",
    "Eric White",
    "Steven Harris",
    "Andrew Clark",
    "Justin Lewis",
    "Nathan Walker",
    "Brian Hall",
]

# Standard stat types (using normalized names)
STAT_TYPES = [
    "Points",
    "Rebounds",
    "Assists",
    "3-PT Made",
    "Pts+Rebs+Asts",
    "Pts+Asts",
    "Pts+Rebs",
    "Steals",
    "Blocked Shots",
    "Turnovers",
]

# Base line values for each stat type (realistic ranges)
STAT_BASELINES = {
    "Points": (15.5, 32.5),
    "Rebounds": (4.5, 12.5),
    "Assists": (3.5, 10.5),
    "3-PT Made": (1.5, 5.5),
    "Pts+Rebs+Asts": (25.5, 55.5),
    "Pts+Asts": (20.5, 40.5),
    "Pts+Rebs": (20.5, 42.5),
    "Steals": (0.5, 2.5),
    "Blocked Shots": (0.5, 3.5),
    "Turnovers": (1.5, 4.5),
}

# Realistic American odds for player props
# Standard odds range from heavy favorites (-200) to slight underdogs (+150)
# Most props are around -110 to -115 (standard juice)
STANDARD_ODDS = [-115, -112, -110, -108, -105]
FAVORITE_ODDS = [-130, -125, -120, -118, -115]
UNDERDOG_ODDS = [+100, +105, +110, +115, +120]
BIG_FAVORITE_ODDS = [-150, -145, -140, -135, -130]
BIG_UNDERDOG_ODDS = [+130, +140, +150, +160, +175]
# Heavy favorites for +EV scenarios (sharp books at these odds = +EV on PrizePicks)
# -180 = 64.3% implied, -200 = 66.7% implied, -220 = 68.8% implied
# 5-Pick Flex only needs 54.25%, so these are all +EV!
HEAVY_FAVORITE_ODDS = [-180, -190, -200, -210, -220, -230, -250]


def get_realistic_odds(base_type='standard', variation=False):
    """
    Generate realistic American odds.

    American odds rules:
    - Negative odds (favorites): -100 to -infinity (e.g., -110, -150, -200)
    - Positive odds (underdogs): +100 to +infinity (e.g., +110, +150, +200)
    - There is NO range between -100 and +100 (e.g., no -80 or +50)

    Args:
        base_type: 'standard', 'favorite', 'underdog', 'big_favorite', 'big_underdog'
        variation: If True, add slight variation to create discrepancies
    """
    odds_pools = {
        'standard': STANDARD_ODDS,
        'favorite': FAVORITE_ODDS,
        'underdog': UNDERDOG_ODDS,
        'big_favorite': BIG_FAVORITE_ODDS,
        'big_underdog': BIG_UNDERDOG_ODDS,
        'heavy_favorite': HEAVY_FAVORITE_ODDS,
    }

    base_odds = random.choice(odds_pools.get(base_type, STANDARD_ODDS))

    if variation:
        # Add variation while keeping odds realistic
        if base_odds < 0:
            # For negative odds, vary by 5-15 points
            adjustment = random.choice([-15, -10, -5, 0, 5, 10, 15])
            new_odds = base_odds + adjustment
            # Ensure we don't go above -100
            if new_odds > -100:
                new_odds = -100
        else:
            # For positive odds, vary by 5-20 points
            adjustment = random.choice([-15, -10, -5, 0, 5, 10, 15, 20])
            new_odds = base_odds + adjustment
            # Ensure we don't go below +100
            if new_odds < 100:
                new_odds = 100
        return new_odds

    return base_odds


def get_opposite_odds(odds):
    """
    Generate the opposite side odds (for under when given over odds).
    In a balanced market, if over is -110, under is also around -110.
    Books add juice, so both sides are typically slightly negative.
    """
    if odds <= -100:
        # If over is favorite, under might be slight underdog or also favorite
        return random.choice([-115, -110, -108, -105, +100, +105])
    else:
        # If over is underdog, under is favorite
        return random.choice([-130, -125, -120, -115, -110])


def ensure_demo_dir():
    """Create the demo directory if it doesn't exist."""
    # demo directory is at project root, not in scripts/
    demo_dir = Path(__file__).parent.parent / 'demo'
    demo_dir.mkdir(exist_ok=True)
    return demo_dir


def generate_demo_data():
    """Generate and populate the demo database with fictional data."""
    print("Setting up demo database...")

    # Ensure demo directory exists
    ensure_demo_dir()

    # Get engine and create tables
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = get_session()
    session = Session()

    try:
        now = datetime.now()

        # Create books
        print("Creating books...")
        pinnacle = Books(
            book_name="Pinnacle",
            book_type="Sports Book",
            scrape_timestamp=now
        )
        prizepicks = Books(
            book_name="PrizePicks",
            book_type="Fantasy",
            scrape_timestamp=now
        )
        draftkings = Books(
            book_name="DraftKings",
            book_type="Sports Book",
            scrape_timestamp=now
        )
        fanduel = Books(
            book_name="FanDuel",
            book_type="Sports Book",
            scrape_timestamp=now
        )
        caesars = Books(
            book_name="Caesars",
            book_type="Sports Book",
            scrape_timestamp=now
        )
        session.add_all([pinnacle, prizepicks, draftkings, fanduel, caesars])
        session.flush()

        # Create matchups (pair up teams)
        print("Creating matchups...")
        matchups = []
        shuffled_teams = FAKE_TEAMS.copy()
        random.shuffle(shuffled_teams)

        for i in range(0, len(shuffled_teams), 2):
            matchup = Matchups(
                home_team=shuffled_teams[i],
                away_team=shuffled_teams[i + 1],
                scrape_timestamp=now
            )
            matchups.append(matchup)
        session.add_all(matchups)
        session.flush()

        # Create props
        print("Creating props...")
        props = {}
        for stat in STAT_TYPES:
            prop = Props(
                category="Player Props",
                units=stat,
                description=f"{stat} Over/Under",
                scrape_timestamp=now
            )
            session.add(prop)
            session.flush()
            props[stat] = prop

        # Create statlines with intentional discrepancies for demo
        print("Creating statlines...")
        statline_count = 0

        for player in FAKE_PLAYERS:
            # Assign player to a random matchup
            matchup = random.choice(matchups)

            # Create lines for a subset of stat types
            player_stats = random.sample(STAT_TYPES, k=random.randint(4, 7))

            for stat in player_stats:
                prop = props[stat]
                baseline = STAT_BASELINES[stat]

                # Generate base points value
                base_points = round(random.uniform(baseline[0], baseline[1]) * 2) / 2  # Round to .5

                # Randomly choose odds type for this prop
                # Include heavy_favorite to create +EV scenarios for PrizePicks parlays
                # Heavy favorites (-180 to -250) imply 64-71% probability, well above 54.25% breakeven
                odds_type = random.choice([
                    'standard', 'standard', 'standard',
                    'favorite', 'favorite',
                    'heavy_favorite', 'heavy_favorite',  # These create +EV on PrizePicks
                    'underdog'
                ])

                # Pinnacle lines (sharp book - reference odds)
                pinnacle_price_over = get_realistic_odds(odds_type)
                pinnacle_price_under = get_opposite_odds(pinnacle_price_over)

                # Over line
                session.add(Statlines(
                    book_id=pinnacle.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(pinnacle_price_over)),
                    points=Decimal(str(base_points)),
                    designation="Over",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # Under line
                session.add(Statlines(
                    book_id=pinnacle.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(pinnacle_price_under)),
                    points=Decimal(str(base_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # DraftKings lines - sometimes different odds to create discrepancies
                if random.random() < 0.3:  # 30% chance of different odds type
                    dk_odds_type = random.choice(['favorite', 'underdog', 'big_favorite', 'big_underdog'])
                    dk_price_over = get_realistic_odds(dk_odds_type)
                else:
                    dk_price_over = get_realistic_odds(odds_type, variation=True)
                dk_price_under = get_opposite_odds(dk_price_over)
                dk_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=draftkings.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(dk_price_over)),
                    points=Decimal(str(dk_points)),
                    designation="Over",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                session.add(Statlines(
                    book_id=draftkings.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(dk_price_under)),
                    points=Decimal(str(dk_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # FanDuel lines - sometimes different odds to create discrepancies
                if random.random() < 0.3:  # 30% chance of different odds type
                    fd_odds_type = random.choice(['favorite', 'underdog', 'big_favorite', 'big_underdog'])
                    fd_price_over = get_realistic_odds(fd_odds_type)
                else:
                    fd_price_over = get_realistic_odds(odds_type, variation=True)
                fd_price_under = get_opposite_odds(fd_price_over)
                fd_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=fanduel.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(fd_price_over)),
                    points=Decimal(str(fd_points)),
                    designation="Over",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                session.add(Statlines(
                    book_id=fanduel.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(fd_price_under)),
                    points=Decimal(str(fd_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # Caesars lines - sometimes different odds to create discrepancies
                if random.random() < 0.3:  # 30% chance of different odds type
                    cs_odds_type = random.choice(['favorite', 'underdog', 'big_favorite', 'big_underdog'])
                    cs_price_over = get_realistic_odds(cs_odds_type)
                else:
                    cs_price_over = get_realistic_odds(odds_type, variation=True)
                cs_price_under = get_opposite_odds(cs_price_over)
                cs_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=caesars.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(cs_price_over)),
                    points=Decimal(str(cs_points)),
                    designation="Over",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                session.add(Statlines(
                    book_id=caesars.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(cs_price_under)),
                    points=Decimal(str(cs_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # PrizePicks line (fantasy app - doesn't have real odds in production)
                # Note: PrizePicks is a fantasy app, not a sportsbook, so in reality
                # they don't expose traditional odds. We include them here for demo
                # purposes but the discrepancies page filters them out.
                pp_price_over = get_realistic_odds(odds_type, variation=True)
                pp_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=prizepicks.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=Decimal(str(pp_price_over)),
                    points=Decimal(str(pp_points)),
                    designation="Over",
                    line_type="demon",
                    scrape_timestamp=now
                ))
                statline_count += 1

        session.commit()
        print(f"\nDemo data generated successfully!")
        print(f"  - Books: 5 (Pinnacle, PrizePicks, DraftKings, FanDuel, Caesars)")
        print(f"  - Matchups: {len(matchups)}")
        print(f"  - Props: {len(props)}")
        print(f"  - Statlines: {statline_count}")
        print(f"\nDatabase saved to: demo/demo.db")

    except Exception as e:
        print(f"Error generating demo data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    generate_demo_data()
