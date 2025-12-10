"""Data scrapers for betting platforms."""
from app.scrapers.pinnacle import scrape as scrape_pinnacle
from app.scrapers.prizepicks import scrape as scrape_prizepicks


def run_all_scrapers():
    """Run all available scrapers sequentially."""
    print("Running Pinnacle scraper...")
    try:
        scrape_pinnacle()
        print("Pinnacle scraper completed.")
    except Exception as e:
        print(f"Pinnacle scraper failed: {e}")

    print("Running PrizePicks scraper...")
    try:
        scrape_prizepicks()
        print("PrizePicks scraper completed.")
    except Exception as e:
        print(f"PrizePicks scraper failed: {e}")


__all__ = ['run_all_scrapers', 'scrape_pinnacle', 'scrape_prizepicks']
