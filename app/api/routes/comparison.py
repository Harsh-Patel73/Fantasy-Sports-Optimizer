"""Line comparison API routes."""
from flask import Blueprint, jsonify, request
from app.api.services.comparison_service import get_line_comparison

comparison_bp = Blueprint('comparison', __name__)


@comparison_bp.route('/compare', methods=['GET'])
def compare_lines():
    """
    Compare lines across books with a primary book focus.

    Shows only lines where the same player+stat exists on multiple books.

    Query Parameters:
        primary_book: Primary book to compare against (required)
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)

    Returns:
        JSON with comparison data:
        {
            "data": [
                {
                    "player_name": "Marcus Johnson",
                    "stat_type": "Points",
                    "matchup": "Team A @ Team B",
                    "primary_line": {"book": "PrizePicks", "points": 25.5, "price": null},
                    "other_lines": [
                        {"book": "Pinnacle", "points": 25.0, "price": -110}
                    ]
                }
            ],
            "meta": {
                "primary_book": "PrizePicks",
                "count": 42
            }
        }
    """
    primary_book = request.args.get('primary_book')

    if not primary_book:
        return jsonify({'error': 'primary_book query parameter is required'}), 400

    result = get_line_comparison(
        primary_book=primary_book,
        team=request.args.get('team'),
        player=request.args.get('player'),
        stat_type=request.args.get('stat_type')
    )

    return jsonify(result)
