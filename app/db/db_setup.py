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

    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}"
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)