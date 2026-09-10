"""Orchestration of router discovery and SSH provisioning."""

from __future__ import annotations

from typing import Callable

import paramiko

from router_controller.router_comms.discovery.bootstrap import (
    RouterBootstrap,
)
from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
    RouterDiscovery,
)
from router_controller.router_comms.discovery.firmware_detector import (
    FirmwareDetector,
)
from router_controller.router_comms.ssh.connection import (
    RouterConnection,
    RouterConnectionConfig,
)
from router_controller.router_comms.ssh.connection_manager import (
    RouterConnectionManager,
)
from router_controller.router_comms.ssh.key_installer import (
    RouterKeyInstaller,
)
from router_controller.router_comms.ssh.keys import (
    SSHKeyManager,
    SSHKeyPair,
)
from router_controller.router_comms.router.router import Router
from router_controller.router_comms.router.repository import (
    RouterStateRepository,
)
from router_controller.router_comms.router.state import RouterState


class RouterProvisioner:
    """Provision a router for controller SSH access.

    The provisioner coordinates discovery, bootstrap authentication,
    key installation, persistent router state, and establishment of
    the permanent key-based SSH connection.
    """


    def __init__(
        self,
        key_manager: SSHKeyManager,
        discovery: RouterDiscovery,
        bootstrap_factory: Callable[
            [RouterCandidate],
            RouterBootstrap,
        ],
        installer_factory: Callable[
            [paramiko.SSHClient],
            RouterKeyInstaller,
        ],
        connection_factory: Callable[
            [RouterCandidate, SSHKeyPair, RouterConnectionConfig],
            RouterConnection,
        ],
        router_repository: RouterStateRepository,
        detector_factory: Callable[
            [RouterConnection],
            FirmwareDetector,
        ] = FirmwareDetector,
    ) -> None:
        self.key_manager = key_manager
        self.discovery = discovery
        self.bootstrap_factory = bootstrap_factory
        self.installer_factory = installer_factory
        self.connection_factory = connection_factory
        self.router_repository = router_repository
        self.detector_factory = detector_factory

    def provision(
        self,
        candidate: RouterCandidate | None = None,
    ) -> Router:
        """Provision a router and verify key-based SSH authentication.

        If ``candidate`` is not supplied, discovery is performed.

        The controller key is loaded when it already exists. If no complete
        key pair exists, a new RSA key pair is generated.

        Bootstrap communication is used only to install the controller's
        public key. The bootstrap connection is always closed before the
        permanent key-based connection is established.
        """

        key_pair = self._load_or_generate_key_pair()

        if candidate is None:
            candidate = self.discovery.discover()

        bootstrap = self.bootstrap_factory(candidate)
        client, credentials = bootstrap.connect()

        try:
            installer = self.installer_factory(client)
            installer.install(key_pair)

            state = self._build_router_state(
                candidate=candidate,
                username=credentials.username,
                fingerprint=credentials.ssh_host_key_fingerprint,
            )

            self.router_repository.save(state)

        finally:
            client.close()

        manager = self.create_connection_manager(
            candidate=candidate,
            key_pair=key_pair,
            state=state,
        )

        connection = manager.connect()

        if not connection.connected:
            raise RuntimeError(
                "Router SSH connection was not established."
            )

        firmware_identity = self.detector_factory(
            connection
        ).detect()


        fingerprint = connection.host_key_fingerprint

        if fingerprint is None:
            raise RuntimeError(
                "Router SSH host key could not be determined."
            )

        return Router.from_connection(
            candidate=candidate,
            host_key_fingerprint=fingerprint,
            state=state,
            connection_manager=manager,
            firmware_identity=firmware_identity
        )

    def _load_or_generate_key_pair(self) -> SSHKeyPair:
        """Load the controller key pair or create it when absent."""

        try:
            return self.key_manager.load_key_pair()
        except FileNotFoundError:
            return self.key_manager.generate_key_pair()

    def create_connection_manager(
        self,
        candidate: RouterCandidate,
        key_pair: SSHKeyPair,
        state: RouterState | None = None,
    ) -> RouterConnectionManager:
        """Create a connection manager for a provisioned router."""

        return RouterConnectionManager(
            candidate=candidate,
            key_pair=key_pair,
            state=state,
            connection_factory=self.connection_factory,
        )

    def _build_router_state(
        self,
        candidate: RouterCandidate,
        username: str,
        fingerprint: str,
    ) -> RouterState:
        """Build persistent state for a newly provisioned router."""
        if candidate.mac_address is None:
            raise RuntimeError(
                "Router MAC address is required before router state can be saved."
            )

        return RouterState(
            mac_address=candidate.mac_address,
            ssh_host_key=fingerprint,
            ip_address=candidate.address,
            ssh_port=candidate.ssh_port,
            username=username,
        )

