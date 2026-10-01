"""Web UI for the Router Pi Controller."""

__version__ = "0.3"

from pathlib import Path

from flask import Flask

from .welcome import register_routes
from .status import register_status_routes

from .layout.status import layout_status_bp
from .layout.manager import LayoutManager


def register_ui_context(app: Flask) -> None:
    """Register values available to all UI templates."""

    @app.context_processor
    def inject_ui_context() -> dict[str, str]:
        """Provide common UI values."""

        return {
            "ui_version": __version__,
        }


def register_status_ui(app: Flask) -> None:
    """Register the existing router status UI."""

    register_status_routes(app)


def register_layout_manager(app: Flask) -> None:
    """Register the layout manager."""

    layouts_path = (
        Path(app.root_path)
        / "ui"
        / "layouts"
    )

    app.extensions["layout_manager"] = LayoutManager(
        layouts_path
    )


def register_layout_ui(app: Flask) -> None:
    """Register the new layout-based UI."""

    app.register_blueprint(
        layout_status_bp
    )
