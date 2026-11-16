from flask import (
    Blueprint,
    current_app,
    render_template,
    send_from_directory,
)

layout_status_bp = Blueprint(
    "layout_status",
    __name__,
    url_prefix="/layout",
)

@layout_status_bp.get("/status")
def status():
    """Render the active layout status page."""

    manager = current_app.extensions["layout_manager"]

    return render_template(
        "status.html",
        tabs=manager.tabs,
        active_tab="dashboard",
    )


@layout_status_bp.get("/gui-config")
def gui_config():
    """Render the GUI configuration page."""

    manager = current_app.extensions["layout_manager"]

    return render_template(
        "gui_config.html",
        tabs=manager.tabs,
        active_tab="gui-config",
    )

@layout_status_bp.get("/static/<path:filename>")
def layout_static(filename):
    """Serve static files from the active layout."""

    manager = current_app.extensions["layout_manager"]
    layout = manager.active()

    if layout is None:
        raise RuntimeError(
            "No active layout is available."
        )

    return send_from_directory(
        layout.path / "static",
        filename,
    )