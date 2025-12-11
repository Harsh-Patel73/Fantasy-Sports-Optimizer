"""Parlay builder API routes."""
from flask import Blueprint, jsonify, request
from app.api.services.parlay_service import (
    find_ev_lines,
    validate_parlay_lines,
    get_available_lines
)
from app.api.services.calculator_service import BREAKEVEN_PROBS

parlay_bp = Blueprint('parlay', __name__)


@parlay_bp.route('/parlay/ev-lines', methods=['GET'])
def get_ev_lines():
    """
    Auto-generate +EV lines for parlay building.

    Finds lines where sharp book odds imply better probability than the
    parlay break-even threshold.

    Query Parameters:
        betting_book: User's betting platform (e.g., 'PrizePicks') - required
        sharp_books: Comma-separated list of sharp books (e.g., 'Pinnacle,DraftKings') - required
        parlay_type: One of '5-pick-flex', '6-pick-flex', '3-pick-flex', '2-pick-power' - required
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)

    Returns:
        JSON with +EV lines sorted by edge (highest first)
    """
    betting_book = request.args.get('betting_book')
    sharp_books_str = request.args.get('sharp_books', '')
    parlay_type = request.args.get('parlay_type')

    if not betting_book:
        return jsonify({'error': 'betting_book is required'}), 400

    if not sharp_books_str:
        return jsonify({'error': 'sharp_books is required (comma-separated)'}), 400

    if not parlay_type:
        return jsonify({
            'error': 'parlay_type is required',
            'valid_types': list(BREAKEVEN_PROBS.keys())
        }), 400

    sharp_books = [b.strip() for b in sharp_books_str.split(',') if b.strip()]

    if not sharp_books:
        return jsonify({'error': 'At least one sharp book is required'}), 400

    result = find_ev_lines(
        betting_book=betting_book,
        sharp_books=sharp_books,
        parlay_type=parlay_type,
        team=request.args.get('team'),
        player=request.args.get('player'),
        stat_type=request.args.get('stat_type')
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@parlay_bp.route('/parlay/validate', methods=['POST'])
def validate_parlay():
    """
    Validate user-selected lines against sharp books.

    Request Body:
    {
        "line_ids": [1, 2, 3],
        "sharp_books": ["Pinnacle", "DraftKings"],
        "parlay_type": "5-pick-flex"
    }

    Returns:
        JSON with validation results for each line, including:
        - is_ev: Whether the line is +EV
        - edge: The edge percentage over break-even
        - sharp_odds: Odds from each sharp book
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    line_ids = data.get('line_ids', [])
    sharp_books = data.get('sharp_books', [])
    parlay_type = data.get('parlay_type')

    if not line_ids:
        return jsonify({'error': 'line_ids is required'}), 400

    if not sharp_books:
        return jsonify({'error': 'sharp_books is required'}), 400

    if not parlay_type:
        return jsonify({
            'error': 'parlay_type is required',
            'valid_types': list(BREAKEVEN_PROBS.keys())
        }), 400

    result = validate_parlay_lines(
        line_ids=line_ids,
        sharp_books=sharp_books,
        parlay_type=parlay_type
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@parlay_bp.route('/parlay/lines', methods=['GET'])
def get_lines_for_selection():
    """
    Get available lines from a betting book for manual selection.

    Query Parameters:
        betting_book: Book to get lines from (required)
        team: Filter by team (optional)
        player: Filter by player name (optional)
        stat_type: Filter by stat type (optional)
        page: Page number (default 1)
        per_page: Items per page (default 50)

    Returns:
        JSON with lines and pagination info
    """
    betting_book = request.args.get('betting_book')

    if not betting_book:
        return jsonify({'error': 'betting_book is required'}), 400

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
    except ValueError:
        return jsonify({'error': 'page and per_page must be integers'}), 400

    result = get_available_lines(
        betting_book=betting_book,
        team=request.args.get('team'),
        player=request.args.get('player'),
        stat_type=request.args.get('stat_type'),
        page=page,
        per_page=per_page
    )

    return jsonify(result)


@parlay_bp.route('/parlay/types', methods=['GET'])
def get_parlay_types():
    """
    Get all available parlay types and their break-even info.

    Returns list of parlay types with break-even probabilities and odds.
    """
    types = []
    for parlay_type, breakeven_prob in BREAKEVEN_PROBS.items():
        types.append({
            'type': parlay_type,
            'breakeven_prob': breakeven_prob,
            'breakeven_percent': round(breakeven_prob * 100, 2),
            'breakeven_odds': round(-100 * breakeven_prob / (1 - breakeven_prob)) if breakeven_prob >= 0.5 else round(100 * (1 - breakeven_prob) / breakeven_prob),
        })

    return jsonify({'parlay_types': types})
