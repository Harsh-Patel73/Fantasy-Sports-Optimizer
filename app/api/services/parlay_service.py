"""
Parlay builder service for finding +EV lines and validating parlays.
"""
from sqlalchemy import func
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props
from app.api.services.calculator_service import BREAKEVEN_PROBS


def american_to_implied_prob(american_odds):
    """Convert American odds to implied probability."""
    if american_odds is None:
        return None
    odds = float(american_odds)
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def implied_prob_to_american(prob):
    """Convert implied probability to American odds."""
    if prob is None or prob <= 0 or prob >= 1:
        return None
    if prob >= 0.5:
        return round(-100 * prob / (1 - prob))
    else:
        return round(100 * (1 - prob) / prob)


def find_ev_lines(betting_book, sharp_books, parlay_type, team=None, player=None, stat_type=None):
    """
    Find lines where sharp book odds imply better probability than break-even.

    A line is +EV if: sharp_implied_prob < breakeven_prob
    (Lower probability from sharp books = better actual odds = +EV for the bettor)

    Args:
        betting_book: User's betting platform (e.g., 'PrizePicks')
        sharp_books: List of sharp book names to compare against (e.g., ['Pinnacle', 'DraftKings'])
        parlay_type: Type of parlay (determines break-even probability)
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)

    Returns:
        Dictionary with +EV lines and metadata
    """
    breakeven_prob = BREAKEVEN_PROBS.get(parlay_type)
    if not breakeven_prob:
        return {
            'error': f'Invalid parlay type: {parlay_type}',
            'valid_types': list(BREAKEVEN_PROBS.keys())
        }

    Session = get_session()
    session = Session()

    try:
        # Build base query with filters
        def build_query(book_names):
            query = (
                session.query(Statlines, Books, Matchups, Props)
                .join(Books, Statlines.book_id == Books.book_id)
                .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
                .join(Props, Statlines.prop_id == Props.prop_id)
                .filter(Books.book_name.in_(book_names))
            )

            if stat_type:
                query = query.filter(func.lower(Props.units) == stat_type.lower())

            if player:
                player_pattern = f"%{player.lower()}%"
                query = query.filter(func.lower(Statlines.player_name).like(player_pattern))

            if team:
                team_pattern = f"%{team.lower()}%"
                query = query.filter(
                    (func.lower(Matchups.home_team).like(team_pattern)) |
                    (func.lower(Matchups.away_team).like(team_pattern))
                )

            return query

        # Get lines from betting book
        betting_lines = build_query([betting_book]).all()

        # Get lines from sharp books
        sharp_lines = build_query(sharp_books).all()

        # Build lookup for sharp book lines: key -> list of {book, price, points}
        sharp_lookup = {}
        for statline, book, matchup, prop in sharp_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (
                statline.player_name.lower().strip(),
                prop.units.lower().strip(),
                statline.designation.lower() if statline.designation else 'over'
            )

            if key not in sharp_lookup:
                sharp_lookup[key] = []

            if statline.price is not None:
                sharp_lookup[key].append({
                    'book': book.book_name,
                    'price': float(statline.price),
                    'points': float(statline.points) if statline.points else None,
                    'implied_prob': american_to_implied_prob(float(statline.price))
                })

        # Find +EV lines from betting book
        ev_lines = []
        seen_keys = set()

        for statline, book, matchup, prop in betting_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (
                statline.player_name.lower().strip(),
                prop.units.lower().strip(),
                statline.designation.lower() if statline.designation else 'over'
            )

            # Skip duplicates
            if key in seen_keys:
                continue
            seen_keys.add(key)

            # Find matching sharp lines
            if key not in sharp_lookup or not sharp_lookup[key]:
                continue

            sharp_data = sharp_lookup[key]

            # Calculate average implied probability across sharp books
            implied_probs = [s['implied_prob'] for s in sharp_data if s['implied_prob'] is not None]
            if not implied_probs:
                continue

            avg_sharp_implied = sum(implied_probs) / len(implied_probs)

            # Calculate edge: positive edge means +EV
            # Edge = breakeven_prob - sharp_implied_prob
            edge = breakeven_prob - avg_sharp_implied

            # Only include lines with positive edge (sharp books say odds are better than break-even)
            if edge > 0:
                ev_lines.append({
                    'id': statline.line_id,
                    'player_name': statline.player_name,
                    'stat_type': prop.units,
                    'points': float(statline.points) if statline.points else None,
                    'designation': statline.designation,
                    'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
                    'betting_book': book.book_name,
                    'edge': round(edge, 4),
                    'edge_percent': round(edge * 100, 2),
                    'sharp_implied_prob': round(avg_sharp_implied, 4),
                    'sharp_implied_percent': round(avg_sharp_implied * 100, 2),
                    'sharp_implied_odds': implied_prob_to_american(avg_sharp_implied),
                    'breakeven_prob': breakeven_prob,
                    'sharp_books_data': sharp_data,
                })

        # Sort by edge (highest first)
        ev_lines.sort(key=lambda x: x['edge'], reverse=True)

        return {
            'data': ev_lines,
            'meta': {
                'betting_book': betting_book,
                'sharp_books': sharp_books,
                'parlay_type': parlay_type,
                'breakeven_prob': breakeven_prob,
                'breakeven_percent': round(breakeven_prob * 100, 2),
                'breakeven_odds': implied_prob_to_american(breakeven_prob),
                'count': len(ev_lines),
                'filters': {
                    'team': team,
                    'player': player,
                    'stat_type': stat_type
                }
            }
        }

    finally:
        session.close()


def validate_parlay_lines(line_ids, sharp_books, parlay_type):
    """
    Validate user-selected lines against sharp books.

    Args:
        line_ids: List of line IDs from the betting book
        sharp_books: List of sharp book names to compare against
        parlay_type: Type of parlay (determines break-even probability)

    Returns:
        Dictionary with validation results for each line
    """
    breakeven_prob = BREAKEVEN_PROBS.get(parlay_type)
    if not breakeven_prob:
        return {
            'error': f'Invalid parlay type: {parlay_type}',
            'valid_types': list(BREAKEVEN_PROBS.keys())
        }

    if not line_ids:
        return {
            'error': 'No line_ids provided',
            'validated_lines': []
        }

    Session = get_session()
    session = Session()

    try:
        # Get the selected lines
        selected_lines = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Statlines.line_id.in_(line_ids))
            .all()
        )

        # Get all sharp book lines
        sharp_lines = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Books.book_name.in_(sharp_books))
            .all()
        )

        # Build sharp lookup
        sharp_lookup = {}
        for statline, book, matchup, prop in sharp_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (
                statline.player_name.lower().strip(),
                prop.units.lower().strip(),
                statline.designation.lower() if statline.designation else 'over'
            )

            if key not in sharp_lookup:
                sharp_lookup[key] = []

            if statline.price is not None:
                sharp_lookup[key].append({
                    'book': book.book_name,
                    'price': float(statline.price),
                    'implied_prob': american_to_implied_prob(float(statline.price))
                })

        # Validate each selected line
        validated_lines = []
        total_edge = 0
        ev_count = 0

        for statline, book, matchup, prop in selected_lines:
            key = (
                statline.player_name.lower().strip(),
                prop.units.lower().strip(),
                statline.designation.lower() if statline.designation else 'over'
            )

            sharp_data = sharp_lookup.get(key, [])

            if sharp_data:
                implied_probs = [s['implied_prob'] for s in sharp_data if s['implied_prob'] is not None]
                if implied_probs:
                    avg_sharp_implied = sum(implied_probs) / len(implied_probs)
                    edge = breakeven_prob - avg_sharp_implied
                    is_ev = edge > 0
                else:
                    avg_sharp_implied = None
                    edge = None
                    is_ev = False
            else:
                avg_sharp_implied = None
                edge = None
                is_ev = False

            if edge is not None:
                total_edge += edge
                if is_ev:
                    ev_count += 1

            validated_lines.append({
                'id': statline.line_id,
                'player_name': statline.player_name,
                'stat_type': prop.units,
                'points': float(statline.points) if statline.points else None,
                'designation': statline.designation,
                'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
                'is_ev': is_ev,
                'edge': round(edge, 4) if edge is not None else None,
                'edge_percent': round(edge * 100, 2) if edge is not None else None,
                'sharp_implied_prob': round(avg_sharp_implied, 4) if avg_sharp_implied is not None else None,
                'sharp_odds': sharp_data,
                'has_sharp_data': len(sharp_data) > 0,
            })

        return {
            'validated_lines': validated_lines,
            'summary': {
                'total_lines': len(validated_lines),
                'ev_lines': ev_count,
                'non_ev_lines': len(validated_lines) - ev_count,
                'average_edge': round(total_edge / len(validated_lines), 4) if validated_lines else 0,
                'average_edge_percent': round((total_edge / len(validated_lines)) * 100, 2) if validated_lines else 0,
            },
            'parlay_type': parlay_type,
            'breakeven_prob': breakeven_prob,
            'sharp_books': sharp_books,
        }

    finally:
        session.close()


def get_available_lines(betting_book, team=None, player=None, stat_type=None, page=1, per_page=50):
    """
    Get available lines from a betting book for manual selection.

    Args:
        betting_book: Book to get lines from
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)
        page: Page number for pagination
        per_page: Items per page

    Returns:
        Dictionary with lines and pagination info
    """
    Session = get_session()
    session = Session()

    try:
        query = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(func.lower(Books.book_name) == betting_book.lower())
        )

        if stat_type:
            query = query.filter(func.lower(Props.units) == stat_type.lower())

        if player:
            player_pattern = f"%{player.lower()}%"
            query = query.filter(func.lower(Statlines.player_name).like(player_pattern))

        if team:
            team_pattern = f"%{team.lower()}%"
            query = query.filter(
                (func.lower(Matchups.home_team).like(team_pattern)) |
                (func.lower(Matchups.away_team).like(team_pattern))
            )

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        results = query.order_by(Statlines.player_name).offset(offset).limit(per_page).all()

        lines = []
        for statline, book, matchup, prop in results:
            lines.append({
                'id': statline.line_id,
                'player_name': statline.player_name,
                'stat_type': prop.units,
                'points': float(statline.points) if statline.points else None,
                'designation': statline.designation,
                'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
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
