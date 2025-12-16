from flask import Blueprint, jsonify, request
from app.api.services.comparison_service import find_discrepancies

discrepancies_bp = Blueprint('discrepancies', __name__)


@discrepancies_bp.route('/discrepancies', methods=['GET'])
def list_discrepancies():
    """
    Find lines where Pinnacle and PrizePicks have significant odds differences.

    Query Parameters:
        min_prob_diff: Minimum implied probability difference in % (default 5)
        stat_type: Filter by stat type
        player: Filter by player name (partial match)
        team: Filter by team name (partial match)
    """
    try:
        min_prob_diff = float(request.args.get('min_prob_diff', 5))
    except ValueError:
        min_prob_diff = 5

    stat_type = request.args.get('stat_type')
    player = request.args.get('player')
    team = request.args.get('team')

    result = find_discrepancies(
        min_prob_diff=min_prob_diff,
        stat_type=stat_type,
        player=player,
        team=team
    )

    return jsonify(result)
