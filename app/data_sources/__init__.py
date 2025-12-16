"""Data sources for BetterBets - API integrations only, no scraping."""
from app.data_sources.theoddsapi import fetch as fetch_theoddsapi


def sync_all_data():
    """Fetch data from all configured API sources."""
    print("Fetching data from The Odds API...")
    try:
        fetch_theoddsapi()
        print("The Odds API fetch completed.")
    except Exception as e:
        print(f"The Odds API fetch failed: {e}")


__all__ = ['sync_all_data', 'fetch_theoddsapi']
