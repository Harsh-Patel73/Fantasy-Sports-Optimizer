import pymysql
from sqlalchemy import create_engine
from app.models.base import Base
from app.models.books import Books
from app.models.statlines import Statlines
from app.models.matchups import Matchups
from app.models.props import Props

def setup_database():
    print("Running Database Setup")
    host = "127.0.0.1"
    user = "root"
    password = "huncho11"
    port = 3306
    database_name = "db1"

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
