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

                # Pinnacle lines (both over and under)
                pinnacle_price_over = Decimal(str(random.choice([-115, -110, -105, 100, 105])))
                pinnacle_price_under = Decimal(str(-220 - int(pinnacle_price_over)))  # Rough juice calculation

                # Over line
                session.add(Statlines(
                    book_id=pinnacle.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=pinnacle_price_over,
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
                    price=pinnacle_price_under,
                    points=Decimal(str(base_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # DraftKings lines (with slight price/points variation from Pinnacle)
                dk_price_over = pinnacle_price_over + Decimal(str(random.choice([-5, -3, 0, 3, 5])))
                dk_price_under = Decimal(str(-220 - int(dk_price_over)))
                dk_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=draftkings.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=dk_price_over,
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
                    price=dk_price_under,
                    points=Decimal(str(dk_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # FanDuel lines (with slight price/points variation from Pinnacle)
                fd_price_over = pinnacle_price_over + Decimal(str(random.choice([-5, -3, 0, 3, 5])))
                fd_price_under = Decimal(str(-220 - int(fd_price_over)))
                fd_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=fanduel.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=fd_price_over,
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
                    price=fd_price_under,
                    points=Decimal(str(fd_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # Caesars lines (with slight price/points variation from Pinnacle)
                cs_price_over = pinnacle_price_over + Decimal(str(random.choice([-5, -3, 0, 3, 5])))
                cs_price_under = Decimal(str(-220 - int(cs_price_over)))
                cs_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=caesars.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=cs_price_over,
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
                    price=cs_price_under,
                    points=Decimal(str(cs_points)),
                    designation="Under",
                    line_type="total",
                    scrape_timestamp=now
                ))
                statline_count += 1

                # PrizePicks line (with intentional variation for discrepancy demo)
                # About 30% of lines will have notable discrepancies
                if random.random() < 0.3:
                    # Create a discrepancy (0.5 to 2.5 points different)
                    diff = random.choice([-2.5, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, 2.5])
                    pp_points = base_points + diff
                else:
                    # Small or no difference
                    pp_points = base_points + random.choice([-0.5, 0, 0, 0, 0.5])

                session.add(Statlines(
                    book_id=prizepicks.book_id,
                    player_name=player,
                    matchup_id=matchup.matchup_id,
                    prop_id=prop.prop_id,
                    price=None,  # PrizePicks doesn't expose prices
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
