from flask import Blueprint, jsonify
from config import get_config
from app.data_sources import get_last_sync

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    config = get_config()
    return jsonify({
        'status': 'healthy',
        'demo_mode': config.DEMO_MODE,
        'database': 'sqlite' if config.DEMO_MODE else 'mysql',
        'last_sync': get_last_sync()
    })
