from sqlalchemy import func
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props


def get_lines(book=None, team=None, player=None, stat_type=None, page=1, per_page=50):
    """
    Get betting lines with optional filters.

    Args:
        book: Filter by book name ('Pinnacle', 'PrizePicks', or None for all)
        team: Filter by team name (matches home or away team)
        player: Filter by player name (partial match)
        stat_type: Filter by stat type (exact match)
        page: Page number for pagination
        per_page: Number of results per page

    Returns:
        Dictionary with data, pagination info
    """
    Session = get_session()
    session = Session()

    try:
        query = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
        )

        # Apply filters
        if book and book.lower() != 'all':
            query = query.filter(func.lower(Books.book_name) == book.lower())

        if team:
            team_lower = f"%{team.lower()}%"
            query = query.filter(
                (func.lower(Matchups.home_team).like(team_lower)) |
                (func.lower(Matchups.away_team).like(team_lower))
            )

        if player:
            player_lower = f"%{player.lower()}%"
            query = query.filter(func.lower(Statlines.player_name).like(player_lower))

        if stat_type:
            query = query.filter(func.lower(Props.units) == stat_type.lower())

        # Get total count before pagination
        total = query.count()

        # Order by most recent first, then by player name
        query = query.order_by(
            Statlines.scrape_timestamp.desc(),
            Statlines.player_name
        )

        # Apply pagination
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()

        # Format results
        lines = []
        for statline, book_obj, matchup, prop in results:
            lines.append({
                'id': statline.line_id,
                'player_name': statline.player_name,
                'book': book_obj.book_name,
                'book_type': book_obj.book_type,
                'home_team': matchup.home_team,
                'away_team': matchup.away_team,
                'stat_type': prop.units,
                'category': prop.category,
                'points': float(statline.points) if statline.points else None,
                'price': float(statline.price) if statline.price else None,
                'designation': statline.designation,
                'line_type': statline.line_type,
                'scrape_timestamp': statline.scrape_timestamp.isoformat() if statline.scrape_timestamp else None
            })

        return {
            'data': lines,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        }

    finally:
        session.close()


def get_line_by_id(line_id):
    """Get a specific line by ID."""
    Session = get_session()
    session = Session()

    try:
        result = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Statlines.line_id == line_id)
            .first()
        )

        if not result:
            return None

        statline, book_obj, matchup, prop = result
        return {
            'id': statline.line_id,
            'player_name': statline.player_name,
            'book': book_obj.book_name,
            'book_type': book_obj.book_type,
            'home_team': matchup.home_team,
            'away_team': matchup.away_team,
            'stat_type': prop.units,
            'category': prop.category,
            'points': float(statline.points) if statline.points else None,
            'price': float(statline.price) if statline.price else None,
            'designation': statline.designation,
            'line_type': statline.line_type,
            'scrape_timestamp': statline.scrape_timestamp.isoformat() if statline.scrape_timestamp else None
        }

    finally:
        session.close()
