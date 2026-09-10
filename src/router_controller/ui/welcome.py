import logging

from flask import jsonify, render_template

from router_controller.router_comms.discovery.initial_connection import discover_and_connect_router

logger = logging.getLogger(__name__)

def register_routes(app, provision_router, welcome_service=None):
    """Register welcome and router setup routes."""

    @app.route("/")
    def index():
        status = welcome_service.get_status()

        return render_template(
            "welcome.html",
            status=status,
        )


    @app.get("/api/router/welcome/status")
    def welcome_status():
        logger.info("Welcome status requested")

        status = welcome_service.get_status()

        return jsonify(
            {
                "router_found": status.router_found,
                "mac_known": status.mac_known,
                "ssh_key_present": status.ssh_key_present,
                "ssh_key_valid": status.ssh_key_valid,
                "ready": status.ready,
                "address": status.address,
                "ssh_port": status.ssh_port,
                "message": status.message,
            }
        )


    @app.get("/api/router/discover")
    def discover_router_endpoint():
        logger.info("Router discovery requested")

        try:
            result = discover_and_connect_router()

            if result.candidate is None:
                return jsonify(
                    {
                        "found": False,
                        "connected": False,
                        "error": (
                            str(result.error)
                            if result.error
                            else "No router discovered."
                        ),
                    }
                ), 404


            return jsonify(
                {
                    "found": True,
                    "connected": result.connected,
                    "address": result.candidate.address,
                    "ssh_port": result.candidate.ssh_port,
                    "mac_address": result.candidate.mac_address,
                }
            )

        except Exception as exc:
            logger.exception("Router discovery failed")

            return jsonify(
                {
                    "found": False,
                    "connected": False,
                    "error": str(exc),
                }
            ), 500


    @app.post("/api/router/provision")
    def provision_router_endpoint():
        logger.info("Router provisioning requested")

        if provision_router is None:
            return jsonify(
                {
                    "success": False,
                    "error": "Provisioning unavailable.",
                }
            ), 503

        try:
            router = provision_router()

            return jsonify(
                {
                    "success": True,
                    "address": router.candidate.address,
                    "ssh_port": router.candidate.ssh_port,
                    "mac_address": router.identity.mac_address,
                    "firmware": (
                        router.firmware_identity.name
                        if router.firmware_identity
                        else None
                    ),
                    "message": ("SSH key installed and connection verified."),
                }
            )

        except Exception as exc:
            logger.exception( "Router provisioning failed")

            return jsonify(
                {
                    "success": False,
                    "error": str(exc),
                }
            ), 500
