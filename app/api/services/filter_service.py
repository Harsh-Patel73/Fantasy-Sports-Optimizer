from sqlalchemy import func, distinct
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props


def get_unique_teams():
    """Get all unique team names from matchups."""
    Session = get_session()
    session = Session()

    try:
        # Get all home teams
        home_teams = session.query(distinct(Matchups.home_team)).filter(
            Matchups.home_team.isnot(None)
        ).all()

        # Get all away teams
        away_teams = session.query(distinct(Matchups.away_team)).filter(
            Matchups.away_team.isnot(None)
        ).all()

        # Combine and deduplicate
        teams = set()
        for (team,) in home_teams:
            if team:
                teams.add(team)
        for (team,) in away_teams:
            if team:
                teams.add(team)

        return sorted(list(teams))

    finally:
        session.close()


def get_unique_players(team=None):
    """Get all unique player names from statlines, optionally filtered by team."""
    Session = get_session()
    session = Session()

    try:
        query = session.query(distinct(Statlines.player_name)).filter(
            Statlines.player_name.isnot(None)
        )

        # Filter by team if provided
        if team:
            from sqlalchemy import or_
            query = query.join(Matchups, Statlines.matchup_id == Matchups.matchup_id).filter(
                or_(
                    Matchups.home_team == team,
                    Matchups.away_team == team
                )
            )

        players = query.order_by(Statlines.player_name).all()
        return [player for (player,) in players if player]

    finally:
        session.close()


def get_unique_stat_types():
    """Get all unique stat types from props."""
    Session = get_session()
    session = Session()

    try:
        stat_types = session.query(distinct(Props.units)).filter(
            Props.units.isnot(None)
        ).order_by(Props.units).all()

        return [stat for (stat,) in stat_types if stat]

    finally:
        session.close()


def get_books():
    """Get all sportsbooks/platforms."""
    Session = get_session()
    session = Session()

    try:
        books = session.query(Books).order_by(Books.book_name).all()

        return [
            {
                'id': book.book_id,
                'name': book.book_name,
                'type': book.book_type
            }
            for book in books
        ]

    finally:
        session.close()
