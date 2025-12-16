"""
Initialize the demo database for BetterBets.

This script sets up the SQLite database schema for demo mode.
Data should be fetched from The Odds API using:
    python main.py

Or to just set up the database without fetching:
    python scripts/seed_demo.py

Usage:
    python scripts/seed_demo.py [--fetch]

Options:
    --fetch    Also fetch data from The Odds API after setup
"""
import os
import sys
from pathlib import Path

# Add project root to path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set demo mode before importing app modules
os.environ['DEMO_MODE'] = 'true'

from app.db.session import get_engine
from app.models.base import Base


def ensure_demo_dir():
    """Create the demo directory if it doesn't exist."""
    demo_dir = Path(__file__).parent.parent / 'demo'
    demo_dir.mkdir(exist_ok=True)
    return demo_dir


def setup_database():
    """Set up the demo database schema."""
    print("Setting up demo database...")

    # Ensure demo directory exists
    ensure_demo_dir()

    # Get engine and create tables
    engine = get_engine()
    Base.metadata.create_all(engine)

    print("Database schema created successfully!")
    print("Database location: demo/demo.db")
    print("\nTo populate with data, run:")
    print("  python main.py")


def fetch_data():
    """Fetch data from The Odds API."""
    from app.data_sources.theoddsapi import fetch
    print("\nFetching data from The Odds API...")
    fetch()


if __name__ == "__main__":
    setup_database()

    if '--fetch' in sys.argv:
        fetch_data()
    else:
        print("\nTip: Use --fetch flag to also fetch data from The Odds API")
