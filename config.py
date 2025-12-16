import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # The Odds API Configuration
    ODDS_API_KEY = os.environ.get('ODDS_API_KEY', '')
    ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4'
    ODDS_API_REGIONS = 'us,us2'  # US regions for American odds
    ODDS_API_ODDS_FORMAT = 'american'


class ProductionConfig(Config):
    """Production configuration using MySQL."""
    DEMO_MODE = False
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'betterbets')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DemoConfig(Config):
    """Demo configuration using SQLite."""
    DEMO_MODE = True
    DB_PATH = BASE_DIR / 'demo' / 'demo.db'

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///{self.DB_PATH}"


def get_config():
    """Return appropriate config based on DEMO_MODE environment variable."""
    demo_mode = os.environ.get('DEMO_MODE', 'false').lower() == 'true'
    return DemoConfig() if demo_mode else ProductionConfig()
