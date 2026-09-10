import logging

from flask import Flask

from .config import Config
from .database import initialize_database
from .logging_config import configure_logging
from .router_comms.factory import create_router_services
from .ui import register_routes, register_ui_context
from .ui.welcome_service import WelcomeService


def create_app(config_class=Config, provision_router=None):
    """Create and configure the Flask application."""

    configure_logging(config_class)

    logger = logging.getLogger(__name__)
    logger.info("Starting Router Pi Controller")

    app = Flask(
        __name__,
        template_folder="ui/templates",
    )

    app.config.from_object(config_class)

    initialize_database(config_class)

    services = create_router_services(config_class)

    if provision_router is None:
        provision_router = services.provisioner.provision

    welcome_service = WelcomeService(
        router_repository=services.router_repository,
        key_manager=services.key_manager,
    )

    register_routes(
        app,
        provision_router,
        welcome_service,
    )

    register_ui_context(app)

    return app
