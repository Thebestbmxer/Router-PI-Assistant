"""Web UI for the Router Pi Controller."""
__version__ = "0.3"

from pathlib import Path
from flask import Flask

from .welcome import register_routes
from .status import register_status_routes

from .layout.status import layout_status_bp
from .layout.manager import LayoutManager

from jinja2 import ChoiceLoader, FileSystemLoader

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

def _configure_layout_template_loader(
    app: Flask,
    manager: LayoutManager,
    ) -> None:
    """Configure templates for the active layout."""

    active_layout = manager.active()

    if active_layout is None:
        raise RuntimeError(
            "No active layout is available."
        )

    base_loader = app.extensions[
        "base_template_loader"
    ]

    template_path = (
        active_layout.path / "templates"
    )

    app.jinja_loader = ChoiceLoader(
        [
            FileSystemLoader(
                str(template_path)
            ),
            base_loader,
        ]
    )

    app.jinja_env.cache.clear()

def register_layout_manager(app: Flask) -> None:
    """Register the layout manager and active layout templates."""
    layouts_path = (
        Path(app.root_path)
        / "ui"
        / "layouts"
    )

    manager = LayoutManager(layouts_path)
    app.extensions["layout_manager"] = manager

    app.extensions["layout_manager"] = manager

    # Preserve the application's original template loader.
    app.extensions["base_template_loader"] = (
        app.jinja_loader
    )

    # Register a function to refresh layout templates.
    app.extensions["refresh_layout_templates"] = (
        lambda: _configure_layout_template_loader(
            app,
            manager,
        )
    )

    _configure_layout_template_loader(
        app,
        manager,
    )

    '''
    active_layout = manager.active()

    if active_layout is None:
        raise RuntimeError(
            "No active layout is available."
        )

    template_path = (active_layout.path / "templates")

    app.jinja_loader = ChoiceLoader(
        [
            FileSystemLoader(
                str(template_path)
            ),
            app.jinja_loader,
        ]
    )
'''

'''
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
'''

def register_layout_ui(app: Flask) -> None:
    """Register the new layout-based UI."""
    app.register_blueprint(layout_status_bp)
