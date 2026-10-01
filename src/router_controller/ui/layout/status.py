from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
)

LAYOUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "layouts"
    / "default"
)

layout_status_bp = Blueprint(
    "layout_status",
    __name__,
    url_prefix="/layout",
    template_folder="../../layouts/default/templates",
)

@layout_status_bp.get("/status")
def status():

    tabs = [
        {
            "id": "status",
            "label": "STATUS",
            "route": "/layout/status",
            "enabled": True,
        },
        {
            "id": "network",
            "label": "NETWORK",
            "route": "/layout/network",
            "enabled": True,
        },
        {
            "id": "wireless",
            "label": "WIRELESS",
            "route": "/layout/wireless",
            "enabled": True,
        },
        {
            "id": "clients",
            "label": "CLIENTS",
            "route": "/layout/clients",
            "enabled": True,
        },
        {
            "id": "gui-config",
            "label": "GUI CONFIG",
            "route": "/gui-config",
            "enabled": True,
        },
    ]

    return render_template(
        "layouts/default/status.html",
        tabs=tabs,
        active_tab="status",
    )

@layout_status_bp.get("/static/<path:filename>")
def layout_static(filename):

    return send_from_directory(
        LAYOUT_PATH / "static",
        filename,
    )