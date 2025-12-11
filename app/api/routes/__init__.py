"""API route blueprints."""
from app.api.routes.health import health_bp
from app.api.routes.lines import lines_bp
from app.api.routes.discrepancies import discrepancies_bp
from app.api.routes.filters import filters_bp
from app.api.routes.comparison import comparison_bp
from app.api.routes.parlay import parlay_bp
from app.api.routes.calculators import calculators_bp

__all__ = [
    'health_bp',
    'lines_bp',
    'discrepancies_bp',
    'filters_bp',
    'comparison_bp',
    'parlay_bp',
    'calculators_bp'
]
