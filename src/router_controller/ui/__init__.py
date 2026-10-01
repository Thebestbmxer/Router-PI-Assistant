"""Web UI for the Router Pi Controller."""

__version__ = "0.3"

from flask import Flask

from .welcome import register_routes
from .status import register_status_routes

def register_ui_context(app: Flask) -> None:
    """Register values available to all UI templates."""

    @app.context_processor
    def inject_ui_context() -> dict[str, str]:
        """Provide common UI values to templates."""

        return {"ui_version": __version__,}

def register_status_ui(app: Flask) -> None:
    """Register the router status UI."""

    register_status_routes(app)