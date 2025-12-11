"""Flask application factory."""
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import get_config


def create_app(config_class=None):
    """Create and configure the Flask application."""
    # Get the static folder path (for serving built React frontend)
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')

    app = Flask(__name__, static_folder=static_folder, static_url_path='')

    if config_class is None:
        config_class = get_config()

    app.config['SECRET_KEY'] = config_class.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config_class.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_class.SQLALCHEMY_TRACK_MODIFICATIONS

    # Enable CORS for development (React dev server)
    CORS(app, origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ])

    # Register API blueprints
    from app.api.routes import (
        health_bp, lines_bp, discrepancies_bp, filters_bp,
        comparison_bp, parlay_bp, calculators_bp
    )

    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(lines_bp, url_prefix='/api')
    app.register_blueprint(discrepancies_bp, url_prefix='/api')
    app.register_blueprint(filters_bp, url_prefix='/api')
    app.register_blueprint(comparison_bp, url_prefix='/api')
    app.register_blueprint(parlay_bp, url_prefix='/api')
    app.register_blueprint(calculators_bp, url_prefix='/api')

    # Serve React frontend (for production - single server deployment)
    @app.route('/')
    def serve_index():
        """Serve the React app's index.html."""
        if os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        return "Frontend not built. Run 'npm run build' in frontend/ directory.", 404

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files or fallback to index.html for SPA routing."""
        # Try to serve the exact file
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)

        # Fallback to index.html for SPA client-side routing
        if os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')

        return "Not found", 404

    return app
