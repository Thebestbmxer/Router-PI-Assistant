
"""Router status web UI and JSON API."""

import logging
from dataclasses import asdict, is_dataclass

from flask import jsonify, render_template

logger = logging.getLogger(__name__)


def _router_metadata(router):
    """Return management metadata without collecting system metrics."""
    candidate = getattr(router, "candidate", None)
    identity = getattr(router, "identity", None)
    firmware_identity = getattr(router, "firmware_identity", None)

    return {
        "address": getattr(candidate, "address", None),
        "ssh_port": getattr(candidate, "ssh_port", None),
        "mac_address": getattr(identity, "mac_address", None),
        "firmware": getattr(firmware_identity, "name", None),
    }


def _serialize_status(status):
    """Convert the existing structured status model to a JSON-ready dict."""
    if not is_dataclass(status) or isinstance(status, type):
        raise TypeError(
            "router.status() must return a dataclass instance"
        )

    return asdict(status)


def register_status_routes(app):
    """Register router status UI and API routes."""

    @app.get("/status")
    def status_page():
        """Render the router status page."""
        return render_template(
            "status.html",
            router=app.extensions.get("router"),
        )

    @app.get("/api/router/status")
    def router_status():
        """Return connection metadata and collected router status."""
        router = app.extensions.get("router")

        if router is None:
            return jsonify({
                "configured": False,
                "connected": False,
                "message": "No router connection is configured.",
                "errors": [],
            }), 503

        try:
            connected = bool(router.connected)
        except Exception:
            logger.exception("Unable to determine router connection state")
            return jsonify({
                "configured": True,
                "connected": False,
                "message": "Unable to determine router connection state.",
                "errors": ["Router connection state is unavailable."],
            }), 503

        if not connected:
            return jsonify({
                "configured": True,
                "connected": False,
                "message": "Router SSH connection is not active.",
                "errors": [],
            }), 503

        data = {
            "configured": True,
            "connected": True,
            **_router_metadata(router),
            "system": None,
            "memory": None,
            "storage": None,
            "temperature": None,
            "errors": [],
            "message": "Router SSH connection is active.",
        }

        try:
            status = router.status()
            status_data = _serialize_status(status)

            # Preserve the API's management metadata and connection state.
            # Status metrics may add fields, but must not override these.
            protected_fields = {
                "configured",
                "connected",
                "address",
                "ssh_port",
                "mac_address",
                "firmware",
                "errors",
                "message",
            }
            data.update({
                key: value
                for key, value in status_data.items()
                if key not in protected_fields
            })

            # Preserve any collector errors while guaranteeing a list.
            collector_errors = status_data.get("errors", [])
            if isinstance(collector_errors, list):
                data["errors"].extend(
                    str(error) for error in collector_errors
                )
            elif collector_errors:
                data["errors"].append(str(collector_errors))

            if data["errors"]:
                data["message"] = (
                    "Router connected; some status information "
                    "is unavailable."
                )

        except Exception:
            logger.exception("Unable to collect router status")
            data["errors"].append(
                "Router status collection failed."
            )
            data["message"] = (
                "Router connected; status collection failed."
            )

        # HTTP 200 means the router is connected and the API responded.
        # Individual metric failures are reported in the errors list.
        return jsonify(data), 200
