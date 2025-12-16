from sqlalchemy import func
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props


def get_all_lines_comparison(books=None, team=None, player=None, stat_type=None):
    """
    Get all lines grouped by player+stat, showing all books side by side.

    Args:
        books: List of book names to filter by (optional, empty list means all)
        team: Filter by team (partial match)
        player: Filter by player name (partial match)
        stat_type: Filter by stat type

    Returns:
        Dictionary with comparison data grouped by player+stat
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

        # Apply books filter (list of book names)
        if books and len(books) > 0:
            query = query.filter(Books.book_name.in_(books))

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

        all_lines = query.all()

        # Group by (player_name, stat_type)
        grouped = {}
        for statline, book_obj, matchup, prop in all_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (statline.player_name.lower().strip(), prop.units.lower().strip())

            if key not in grouped:
                grouped[key] = {
                    'player_name': statline.player_name,
                    'stat_type': prop.units,
                    'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
                    'lines': []
                }

            # Avoid duplicate book entries for same player+stat
            existing_books = [l['book'] for l in grouped[key]['lines']]
            if book_obj.book_name not in existing_books:
                grouped[key]['lines'].append({
                    'book': book_obj.book_name,
                    'book_type': book_obj.book_type,
                    'points': float(statline.points) if statline.points else None,
                    'price': float(statline.price) if statline.price else None,
                    'designation': statline.designation,
                })

        # Convert to list and filter to only include entries with multiple books
        comparisons = []
        for data in grouped.values():
            if len(data['lines']) >= 1:  # Show all lines, even single book
                # Sort lines by book name for consistent display
                data['lines'].sort(key=lambda x: x['book'])
                comparisons.append(data)

        # Sort by player name
        comparisons.sort(key=lambda x: x['player_name'])

        return {
            'data': comparisons,
            'meta': {
                'count': len(comparisons),
                'filters': {
                    'books': books,
                    'stat_type': stat_type,
                    'player': player,
                    'team': team
                }
            }
        }

    finally:
        session.close()


def get_line_comparison(primary_book, team=None, player=None, stat_type=None):
    """
    Get side-by-side line comparison with a primary book.

    Shows only lines where the same player+stat exists on multiple books.

    Args:
        primary_book: Name of the primary book to compare against (required)
        team: Filter by team (partial match)
        player: Filter by player name (partial match)
        stat_type: Filter by stat type

    Returns:
        Dictionary with comparison data and metadata:
        {
            'data': [
                {
                    'player_name': 'Marcus Johnson',
                    'stat_type': 'Points',
                    'matchup': 'Team A @ Team B',
                    'primary_line': {'book': 'PrizePicks', 'points': 25.5, 'price': None},
                    'other_lines': [
                        {'book': 'Pinnacle', 'points': 25.0, 'price': -110},
                        {'book': 'DraftKings', 'points': 25.5, 'price': -115},
                    ]
                }
            ],
            'meta': {...}
        }
    """
    Session = get_session()
    session = Session()

    try:
        # Base query for all lines
        def build_query(book_filter=None):
            query = (
                session.query(Statlines, Books, Matchups, Props)
                .join(Books, Statlines.book_id == Books.book_id)
                .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
                .join(Props, Statlines.prop_id == Props.prop_id)
            )

            if book_filter:
                query = query.filter(func.lower(Books.book_name) == book_filter.lower())

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

        # Get primary book lines
        primary_lines = build_query(primary_book).all()

        # Get all other books' lines
        other_lines = build_query().filter(
            func.lower(Books.book_name) != primary_book.lower()
        ).all()

        # Build lookup for other books: key -> list of lines from different books
        other_lookup = {}
        for statline, book, matchup, prop in other_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (statline.player_name.lower().strip(), prop.units.lower().strip())

            if key not in other_lookup:
                other_lookup[key] = []

            other_lookup[key].append({
                'book': book.book_name,
                'points': float(statline.points) if statline.points else None,
                'price': float(statline.price) if statline.price else None,
                'designation': statline.designation,
            })

        # Build comparison results
        comparisons = []
        seen_keys = set()

        for statline, book, matchup, prop in primary_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (statline.player_name.lower().strip(), prop.units.lower().strip())

            # Skip if we've already processed this player+stat
            if key in seen_keys:
                continue

            # Only include if there are matching lines on other books
            if key not in other_lookup:
                continue

            seen_keys.add(key)

            comparisons.append({
                'player_name': statline.player_name,
                'stat_type': prop.units,
                'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
                'designation': statline.designation,
                'primary_line': {
                    'book': book.book_name,
                    'points': float(statline.points) if statline.points else None,
                    'price': float(statline.price) if statline.price else None,
                },
                'other_lines': other_lookup[key],
            })

        # Sort by player name
        comparisons.sort(key=lambda x: x['player_name'])

        return {
            'data': comparisons,
            'meta': {
                'primary_book': primary_book,
                'count': len(comparisons),
                'filters': {
                    'stat_type': stat_type,
                    'player': player,
                    'team': team
                }
            }
        }

    finally:
        session.close()


def american_to_implied_prob(odds):
    """
    Convert American odds to implied probability.

    Args:
        odds: American odds (e.g., -110, +180)

    Returns:
        Implied probability as decimal (0-1) or None if odds is None
    """
    if odds is None:
        return None
    odds = float(odds)
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def find_discrepancies(min_prob_diff=5, stat_type=None, player=None, team=None):
    """
    Find lines where sportsbooks have significant odds differences.

    Only compares actual sportsbooks (book_type='Sports Book'), excluding
    fantasy/DFS apps like PrizePicks and Underdog which don't have traditional odds.

    Algorithm:
    1. Get latest lines from all sportsbooks
    2. Group by (player_name, stat_type) - normalized to lowercase
    3. For each player+stat, find all pairs of books with lines within ±2 points
    4. Compare implied probabilities from odds
    5. Return pairs where probability difference >= min_prob_diff

    Args:
        min_prob_diff: Minimum implied probability difference in % (default 5)
        stat_type: Filter by stat type
        player: Filter by player name (partial match)
        team: Filter by team (partial match)

    Returns:
        Dictionary with discrepancy data and metadata
    """
    Session = get_session()
    session = Session()

    try:
        # Get all lines from sportsbooks only (exclude fantasy apps)
        query = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Books.book_type == "Sports Book")
        )

        # Apply filters
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

        all_lines = query.all()

        # Group lines by (player_name_lower, stat_type_lower)
        lines_by_key = {}
        for statline, book, matchup, prop in all_lines:
            if not statline.player_name or not prop.units:
                continue
            if statline.points is None or statline.price is None:
                continue

            key = (statline.player_name.lower().strip(), prop.units.lower().strip())

            if key not in lines_by_key:
                lines_by_key[key] = []

            lines_by_key[key].append({
                'book_name': book.book_name,
                'player_name': statline.player_name,
                'stat_type': prop.units,
                'points': float(statline.points),
                'odds': float(statline.price),
                'matchup': matchup,
            })

        # Find discrepancies by comparing all pairs of books for each player+stat
        discrepancies = []
        seen_pairs = set()

        for key, lines in lines_by_key.items():
            if len(lines) < 2:
                continue

            # Compare all pairs of different books
            for i, line1 in enumerate(lines):
                for line2 in lines[i + 1:]:
                    # Skip if same book (could be duplicate entries)
                    if line1['book_name'] == line2['book_name']:
                        continue

                    # Create a unique pair key to avoid duplicates
                    pair_key = tuple(sorted([
                        f"{line1['book_name']}:{key[0]}:{key[1]}",
                        f"{line2['book_name']}:{key[0]}:{key[1]}"
                    ]))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    # Only compare if lines are within ±2 points
                    line_diff = abs(line1['points'] - line2['points'])
                    if line_diff > 2:
                        continue

                    # Calculate implied probabilities
                    implied1 = american_to_implied_prob(line1['odds'])
                    implied2 = american_to_implied_prob(line2['odds'])

                    if implied1 is None or implied2 is None:
                        continue

                    prob_diff = abs(implied1 - implied2) * 100

                    if prob_diff >= min_prob_diff:
                        # Determine which book has better odds (lower implied = better for bettor)
                        if implied1 < implied2:
                            better_book, worse_book = line1, line2
                            better_implied, worse_implied = implied1, implied2
                        else:
                            better_book, worse_book = line2, line1
                            better_implied, worse_implied = implied2, implied1

                        matchup = line1['matchup']
                        discrepancies.append({
                            'player_name': line1['player_name'],
                            'stat_type': line1['stat_type'],
                            'matchup': f"{matchup.away_team} @ {matchup.home_team}" if matchup.home_team else "Unknown",
                            'book1_name': better_book['book_name'],
                            'book1_line': better_book['points'],
                            'book1_odds': int(better_book['odds']),
                            'book1_implied': round(better_implied * 100, 1),
                            'book2_name': worse_book['book_name'],
                            'book2_line': worse_book['points'],
                            'book2_odds': int(worse_book['odds']),
                            'book2_implied': round(worse_implied * 100, 1),
                            'prob_difference': round(prob_diff, 1),
                            'line_difference': round(line_diff, 1),
                        })

        # Sort by probability difference (largest first)
        discrepancies.sort(key=lambda x: x['prob_difference'], reverse=True)

        return {
            'data': discrepancies,
            'meta': {
                'min_prob_diff_applied': min_prob_diff,
                'count': len(discrepancies),
                'filters': {
                    'stat_type': stat_type,
                    'player': player,
                    'team': team
                }
            }
        }

    finally:
        session.close()
