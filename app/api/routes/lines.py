from flask import Blueprint, jsonify, request
from app.api.services.line_service import get_lines, get_line_by_id

lines_bp = Blueprint('lines', __name__)


@lines_bp.route('/lines', methods=['GET'])
def list_lines():
    """
    Get betting lines with optional filters.

    Query Parameters:
        book: Filter by book name (pinnacle, prizepicks, or all)
        team: Filter by team name (partial match)
        player: Filter by player name (partial match)
        stat_type: Filter by stat type
        page: Page number (default 1)
        per_page: Results per page (default 50, max 100)
    """
    book = request.args.get('book')
    team = request.args.get('team')
    player = request.args.get('player')
    stat_type = request.args.get('stat_type')

    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
    except ValueError:
        page = 1
        per_page = 50

    result = get_lines(
        book=book,
        team=team,
        player=player,
        stat_type=stat_type,
        page=page,
        per_page=per_page
    )

    return jsonify(result)


@lines_bp.route('/lines/<int:line_id>', methods=['GET'])
def get_line(line_id):
    """Get a specific line by ID."""
    result = get_line_by_id(line_id)

    if result is None:
        return jsonify({'error': 'Line not found'}), 404

    return jsonify(result)
