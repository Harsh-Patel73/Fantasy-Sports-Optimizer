"""Line comparison API routes."""
from flask import Blueprint, jsonify, request
from app.api.services.comparison_service import get_all_lines_comparison

comparison_bp = Blueprint('comparison', __name__)


@comparison_bp.route('/compare', methods=['GET'])
def compare_lines():
    """
    Get all lines grouped by player+stat, showing all books side by side.

    Query Parameters:
        books: Comma-separated list of book names to filter by (optional, empty means all)
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)

    Returns:
        JSON with comparison data grouped by player+stat
    """
    # Parse books from comma-separated string to list
    books_param = request.args.get('books')
    books = None
    if books_param:
        books = [b.strip() for b in books_param.split(',') if b.strip()]

    result = get_all_lines_comparison(
        books=books,
        team=request.args.get('team'),
        player=request.args.get('player'),
        stat_type=request.args.get('stat_type')
    )

    return jsonify(result)
