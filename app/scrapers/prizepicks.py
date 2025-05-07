import requests
from datetime import datetime
from decimal import Decimal
from app.db.session import SessionLocal
from app.models.books import Books
from app.models.statlines import Statlines
from app.models.matchups import Matchups
from app.models.props import Props

