import pymysql
from sqlalchemy import create_engine
from app.models import Base, Books, Matchups, Props, Statlines
from config import get_config


def setup_database():
    print("Running Database Setup")
    config = get_config()

    # In demo mode, just create SQLite tables
    if config.DEMO_MODE:
        from app.db.session import get_engine
        engine = get_engine()
        print("Creating SQLite tables for demo mode...")
        Base.metadata.create_all(engine)
        print("Database setup complete.")
        return

    # Production mode: MySQL setup
    host = config.DB_HOST
    user = config.DB_USER
    password = config.DB_PASSWORD
    port = int(config.DB_PORT)
    database_name = config.DB_NAME

    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database '{database_name}' created or already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        connection.close()

    # Database connection URL
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}"
    engine = create_engine(DATABASE_URL, echo=True)

    # Drop all existing tables in the database
    print("Dropping all tables in the database...")
    Base.metadata.drop_all(engine)  # Drop all tables

    # Create all tables again
    print("Creating all tables...")
    Base.metadata.create_all(engine)  # Create all tables

    print("Database setup complete.")

