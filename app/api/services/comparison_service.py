from sqlalchemy import func
from app.db.session import get_session
from app.models.statlines import Statlines
from app.models.books import Books
from app.models.matchups import Matchups
from app.models.props import Props


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
