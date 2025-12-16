"""Data sources for BetterBets - API integrations only, no scraping."""
import os
from datetime import datetime
from pathlib import Path
from app.data_sources.theoddsapi import fetch as fetch_theoddsapi

# Path to store last sync timestamp
LAST_SYNC_FILE = Path(__file__).parent / 'last_sync.txt'


def get_last_sync():
    """Get the last sync timestamp as ISO string, or None if never synced."""
    if LAST_SYNC_FILE.exists():
        try:
            return LAST_SYNC_FILE.read_text().strip()
        except Exception:
            return None
    return None


def _save_sync_timestamp():
    """Save current timestamp to file."""
    try:
        timestamp = datetime.utcnow().isoformat() + 'Z'
        LAST_SYNC_FILE.write_text(timestamp)
    except Exception as e:
        print(f"Warning: Could not save sync timestamp: {e}")


def sync_all_data():
    """Fetch data from all configured API sources."""
    print("Fetching data from The Odds API...")
    try:
        fetch_theoddsapi()
        print("The Odds API fetch completed.")
        _save_sync_timestamp()
    except Exception as e:
        print(f"The Odds API fetch failed: {e}")


__all__ = ['sync_all_data', 'fetch_theoddsapi', 'get_last_sync']
