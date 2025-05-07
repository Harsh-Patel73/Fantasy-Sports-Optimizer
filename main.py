from app.scrapers import pinnacle
from app.db.db_setup import setup_database

def run_all():
    print("Setting up database")
    setup_database()
    print("Running all scrapers")

    try: 
        pinnacle.scrape()
    except Exception as e:
        print(f"Pinnacle scrape failed: {e}")


if __name__ == "__main__":
    run_all()

