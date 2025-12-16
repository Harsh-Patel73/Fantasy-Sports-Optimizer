from flask import Blueprint, jsonify, request
from app.api.services.filter_service import (
    get_unique_teams,
    get_unique_players,
    get_unique_stat_types,
    get_books
)

filters_bp = Blueprint('filters', __name__)


@filters_bp.route('/filters/teams', methods=['GET'])
def list_teams():
    """Get all unique team names for filter dropdown."""
    teams = get_unique_teams()
    return jsonify({'data': teams})


@filters_bp.route('/filters/players', methods=['GET'])
def list_players():
    """Get all unique player names for filter dropdown.

    Query Parameters:
        team: Filter players by team (optional)
    """
    team = request.args.get('team')
    players = get_unique_players(team=team)
    return jsonify({'data': players})


@filters_bp.route('/filters/stat-types', methods=['GET'])
def list_stat_types():
    """Get all unique stat types for filter dropdown."""
    stat_types = get_unique_stat_types()
    return jsonify({'data': stat_types})


@filters_bp.route('/books', methods=['GET'])
def list_books():
    """Get all sportsbooks/platforms."""
    books = get_books()
    return jsonify({'data': books})
