"""Calculator API routes."""
from flask import Blueprint, jsonify, request
from app.api.services.calculator_service import (
    devig_two_way,
    calculate_parlay_breakeven,
    PAYOUT_STRUCTURES
)

calculators_bp = Blueprint('calculators', __name__)


@calculators_bp.route('/calculators/devig', methods=['POST'])
def devig():
    """Remove vig from two-way betting lines.

    Request Body:
    {
        "odds_1": -110,
        "odds_2": -110,
        "method": "multiplicative"  // or "additive", "power"
    }

    Returns:
    {
        "true_prob_1": 0.50,
        "true_prob_2": 0.50,
        "fair_odds_1": 100,
        "fair_odds_2": 100,
        "total_vig": 4.55
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    odds_1 = data.get('odds_1')
    odds_2 = data.get('odds_2')
    method = data.get('method', 'multiplicative')

    if odds_1 is None or odds_2 is None:
        return jsonify({'error': 'Both odds_1 and odds_2 are required'}), 400

    try:
        odds_1 = int(odds_1)
        odds_2 = int(odds_2)
    except (ValueError, TypeError):
        return jsonify({'error': 'Odds must be integers'}), 400

    if method not in ['multiplicative', 'additive', 'power']:
        return jsonify({
            'error': f'Invalid method: {method}',
            'valid_methods': ['multiplicative', 'additive', 'power']
        }), 400

    try:
        result = devig_two_way(odds_1, odds_2, method)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calculators_bp.route('/calculators/parlay-odds', methods=['POST'])
def parlay_odds():
    """Calculate break-even probability and odds for PrizePicks-style parlays.

    Request Body:
    {
        "parlay_type": "5-pick-flex"
    }

    Valid parlay types: 5-pick-flex, 6-pick-flex, 3-pick-flex, 2-pick-power

    Returns:
    {
        "parlay_type": "5-pick-flex",
        "total_picks": 5,
        "payout_structure": {"5": 10, "4": 2, "3": 0.4},
        "breakeven_prob": 0.5425,
        "breakeven_percent": 54.25,
        "breakeven_odds": -119
    }
    """
    data = request.get_json()
    parlay_type = data.get('parlay_type') if data else None

    if not parlay_type:
        return jsonify({
            'error': 'parlay_type is required',
            'valid_types': list(PAYOUT_STRUCTURES.keys())
        }), 400

    result = calculate_parlay_breakeven(parlay_type)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@calculators_bp.route('/calculators/parlay-types', methods=['GET'])
def get_parlay_types():
    """Get all available parlay types and their payout structures.

    Returns list of parlay types with their payout info.
    """
    types = []
    for parlay_type, payouts in PAYOUT_STRUCTURES.items():
        result = calculate_parlay_breakeven(parlay_type)
        types.append({
            'type': parlay_type,
            'total_picks': result['total_picks'],
            'payout_structure': payouts,
            'breakeven_percent': result['breakeven_percent'],
            'breakeven_odds': result['breakeven_odds'],
        })

    return jsonify({'parlay_types': types})
