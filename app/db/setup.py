from app.models import Base
from app.db.session import get_engine
from config import get_config


def setup_database():
    """Set up the database tables."""
    print("Running Database Setup")
    config = get_config()

    engine = get_engine()

    if config.DEMO_MODE:
        print("Creating SQLite tables...")
    else:
        print("Creating MySQL tables...")

    Base.metadata.create_all(engine)
    print("Database setup complete.")

