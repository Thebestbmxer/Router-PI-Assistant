
"""Router status web UI."""

import logging
from dataclasses import asdict

from flask import jsonify, render_template

logger = logging.getLogger(__name__)


def register_status_routes(app):
    """Register router status UI and API routes."""

    @app.get("/status")
    def status_page():
        """Render the router status page."""
        router = app.extensions.get("router")

        return render_template(
            "status.html",
            router=router,
        )

    @app.get("/api/router/status")
    def router_status():
        """Return router connection and system status as JSON."""
        router = app.extensions.get("router")

        if router is None:
            return jsonify(
                {
                    "configured": False,
                    "connected": False,
                    "message": "No router connection is active.",
                    "errors": [],
                }
            ), 503

        if not router.connected:
            return jsonify(
                {
                    "configured": True,
                    "connected": False,
                    "message": "Router SSH connection is not active.",
                    "errors": [],
                }
            ), 503

        data = {
            "configured": True,
            "connected": True,
            "address": router.candidate.address,
            "ssh_port": router.candidate.ssh_port,
            "mac_address": router.identity.mac_address,
            "firmware": (
                router.firmware_identity.name
                if router.firmware_identity
                else None
            ),
            "system": None,
            "errors": [],
            "message": "Router SSH connection is active.",
        }

        try:
            status = router.status()
            status_data = asdict(status)
            data.update(status_data)

        except Exception:
            logger.exception("Unable to collect router status")
            data["errors"].append(
                "Router metrics are temporarily unavailable."
            )

        return jsonify(data)
