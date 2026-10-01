"""Reconnect to an already-provisioned router."""

from __future__ import annotations

import logging
from typing import Callable

from router_controller.router_comms.discovery.firmware_detector import (
    FirmwareDetector,
    FirmwareIdentity,
)
from router_controller.router_comms.discovery.router_discovery import RouterCandidate
from router_controller.router_comms.router.router import Router
from router_controller.router_comms.router.repository import RouterStateRepository
from router_controller.router_comms.router.state import RouterState
from router_controller.router_comms.ssh.connection import (
    RouterConnection,
    RouterConnectionConfig,
)
from router_controller.router_comms.ssh.connection_manager import RouterConnectionManager
from router_controller.router_comms.ssh.keys import (
    SSHKeyManager,
    SSHKeyPair,
)

logger = logging.getLogger(__name__)


class ExistingRouterConnection:
    """Reconnect to a previously provisioned router.

    This class never installs an SSH key and never performs bootstrap
    authentication. It only uses the persisted router state and the
    controller's existing SSH key to establish the normal key-based
    connection.
    """

    def __init__(
        self,
        key_manager: SSHKeyManager,
        router_repository: RouterStateRepository,
        connection_factory: Callable[
            [RouterCandidate, SSHKeyPair, RouterConnectionConfig],
            RouterConnection,
        ],
        detector_factory: Callable[
            [RouterConnection],
            FirmwareDetector,
        ] = FirmwareDetector,
    ) -> None:
        self.key_manager = key_manager
        self.router_repository = router_repository
        self.connection_factory = connection_factory
        self.detector_factory = detector_factory

    def connect(self) -> Router | None:
        """Attempt to reconnect to the previously provisioned router.

        Returns:
            Router: When a key-based SSH connection is established.
            None: When no router is configured or connection fails.

        This method intentionally does not raise connection failures.
        The controller must remain available even when the router is
        powered off or temporarily unreachable.
        """

        state = self.router_repository.load()

        if state is None:
            logger.info(
                "No persisted router state found; "
                "existing router connection unavailable."
            )
            return None

        try:
            key_pair = self.key_manager.load_key_pair()
        except FileNotFoundError:
            logger.warning(
                "Persisted router state exists, but the SSH key pair "
                "is unavailable."
            )
            return None

        candidate = RouterCandidate(
            address=state.ip_address,
            ssh_port=state.ssh_port,
            mac_address=state.mac_address,
        )

        manager = RouterConnectionManager(
            candidate=candidate,
            key_pair=key_pair,
            state=state,
            connection_factory=self.connection_factory,
        )

        try:
            connection = manager.connect()

            if not connection.connected:
                logger.warning("Existing router connection was not established.")
                return None

            fingerprint = connection.host_key_fingerprint

            if fingerprint is None:
                logger.warning(
                    "Router SSH connection succeeded, but no "
                    "host key fingerprint was available."
                )
                manager.disconnect()
                return None

            firmware_identity = self.detector_factory(connection).detect()

            router = Router.from_connection(
                candidate=candidate,
                host_key_fingerprint=fingerprint,
                state=state,
                connection_manager=manager,
                firmware_identity=firmware_identity,
            )

            logger.info(
                "Existing router connection established: %s",
                candidate.address,
            )

            return router

        except Exception:
            logger.exception(
                "Unable to reconnect to existing router at %s",
                state.ip_address,
            )

            manager.disconnect()

            return None
