from sqlalchemy import func
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props


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


def find_discrepancies(min_diff=0.5, stat_type=None, player=None, team=None):
    """
    Find lines where Pinnacle and PrizePicks differ significantly.

    Algorithm:
    1. Get latest lines from each book
    2. Group by (player_name, stat_type) - normalized to lowercase
    3. Compare points values between books
    4. Return matches where |pinnacle_points - prizepicks_points| >= min_diff

    Args:
        min_diff: Minimum point difference to include (default 0.5)
        stat_type: Filter by stat type
        player: Filter by player name (partial match)
        team: Filter by team (partial match)

    Returns:
        Dictionary with discrepancy data and metadata
    """
    Session = get_session()
    session = Session()

    try:
        # Get all Pinnacle lines
        pinnacle_query = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Books.book_name == "Pinnacle")
        )

        # Get all PrizePicks lines
        prizepicks_query = (
            session.query(Statlines, Books, Matchups, Props)
            .join(Books, Statlines.book_id == Books.book_id)
            .join(Matchups, Statlines.matchup_id == Matchups.matchup_id)
            .join(Props, Statlines.prop_id == Props.prop_id)
            .filter(Books.book_name == "PrizePicks")
        )

        # Apply common filters
        if stat_type:
            pinnacle_query = pinnacle_query.filter(func.lower(Props.units) == stat_type.lower())
            prizepicks_query = prizepicks_query.filter(func.lower(Props.units) == stat_type.lower())

        if player:
            player_pattern = f"%{player.lower()}%"
            pinnacle_query = pinnacle_query.filter(func.lower(Statlines.player_name).like(player_pattern))
            prizepicks_query = prizepicks_query.filter(func.lower(Statlines.player_name).like(player_pattern))

        if team:
            team_pattern = f"%{team.lower()}%"
            pinnacle_query = pinnacle_query.filter(
                (func.lower(Matchups.home_team).like(team_pattern)) |
                (func.lower(Matchups.away_team).like(team_pattern))
            )
            prizepicks_query = prizepicks_query.filter(
                (func.lower(Matchups.home_team).like(team_pattern)) |
                (func.lower(Matchups.away_team).like(team_pattern))
            )

        pinnacle_lines = pinnacle_query.all()
        prizepicks_lines = prizepicks_query.all()

        # Build lookup by (player_name_lower, stat_type_lower)
        pinnacle_lookup = {}
        for statline, book, matchup, prop in pinnacle_lines:
            if statline.player_name and prop.units:
                key = (statline.player_name.lower().strip(), prop.units.lower().strip())
                # Keep the first one (or could keep latest by timestamp)
                if key not in pinnacle_lookup:
                    pinnacle_lookup[key] = {
                        'statline': statline,
                        'matchup': matchup,
                        'prop': prop
                    }

        # Find discrepancies
        discrepancies = []
        for statline, book, matchup, prop in prizepicks_lines:
            if not statline.player_name or not prop.units:
                continue

            key = (statline.player_name.lower().strip(), prop.units.lower().strip())

            if key in pinnacle_lookup:
                pinnacle_data = pinnacle_lookup[key]
                pinnacle_statline = pinnacle_data['statline']
                pinnacle_matchup = pinnacle_data['matchup']

                if pinnacle_statline.points is None or statline.points is None:
                    continue

                pinnacle_points = float(pinnacle_statline.points)
                prizepicks_points = float(statline.points)
                diff = abs(pinnacle_points - prizepicks_points)

                if diff >= min_diff:
                    # Calculate percentage difference
                    base = pinnacle_points if pinnacle_points != 0 else 1
                    percent_diff = round((diff / base) * 100, 1)

                    # Determine which is higher
                    higher_book = "PrizePicks" if prizepicks_points > pinnacle_points else "Pinnacle"

                    discrepancies.append({
                        'player_name': statline.player_name,
                        'stat_type': prop.units,
                        'pinnacle_line': pinnacle_points,
                        'prizepicks_line': prizepicks_points,
                        'difference': round(diff, 1),
                        'percent_diff': percent_diff,
                        'higher_book': higher_book,
                        'matchup': f"{pinnacle_matchup.away_team} @ {pinnacle_matchup.home_team}" if pinnacle_matchup.home_team else "Unknown",
                        'pinnacle_price': float(pinnacle_statline.price) if pinnacle_statline.price else None,
                    })

        # Sort by difference (largest first)
        discrepancies.sort(key=lambda x: x['difference'], reverse=True)

        return {
            'data': discrepancies,
            'meta': {
                'min_diff_applied': min_diff,
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
