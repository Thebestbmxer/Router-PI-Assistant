"""Router device representation."""
from dataclasses import dataclass, field

from router_controller.firmware_status_providers.registry import ProviderRegistry
from router_controller.firmware_status_providers.provider import StatusProvider

from router_controller.router_comms.discovery.firmware_detector import FirmwareIdentity
from router_controller.router_comms.discovery.router_discovery import RouterCandidate

from router_controller.router_comms.router.identity import RouterIdentity
from router_controller.router_comms.router.state import RouterState

from router_controller.router_comms.ssh.connection_manager import RouterConnectionManager
from router_controller.router_comms.ssh.keys import SSHKeyPair

@dataclass
class Router:
    """A known router managed by the controller."""
    identity: RouterIdentity
    candidate: RouterCandidate

    name: str | None = None
    model: str | None = None
    architecture: str | None = None
    target: str | None = None

    state: RouterState | None = None

    firmware_identity: FirmwareIdentity | None = field(default=None)
    connection_manager: RouterConnectionManager | None = field(
        default=None,
        repr=False,
    )

    status_provider: StatusProvider | None = field(
        default=None,
        repr=False,
    )

    def create_connection_manager(
        self,
        key_pair: SSHKeyPair,
    ) -> RouterConnectionManager:
        """Create the SSH connection manager for this router."""
        manager = RouterConnectionManager(
            candidate=self.candidate,
            key_pair=key_pair,
            state=self.state,
        )

        self.connection_manager = manager
        return manager

    @property
    def connected(self) -> bool:
        """Return whether the router currently has an active SSH connection."""
        return (
            self.connection_manager is not None
            and self.connection_manager.connected
        )

    @classmethod
    def from_connection(
        cls,
        candidate: RouterCandidate,
        host_key_fingerprint: str,
        state: RouterState | None = None,
        connection_manager: RouterConnectionManager | None = None,
        firmware_identity: FirmwareIdentity | None = None,
    ) -> "Router":
        """Create a router from a verified SSH connection."""

        identity = RouterIdentity(
            mac_address=candidate.mac_address,
            ssh_host_key_fingerprint=host_key_fingerprint,
        )

        return cls(
            identity=identity,
            candidate=candidate,
            state=state,
            connection_manager=connection_manager,
            firmware_identity=firmware_identity,
        )

    @property
    def firmware_status_provider(self) -> StatusProvider:
        """
        Return the firmware-specific status provider.

        Provider creation is delayed until an authenticated
        SSH connection exists.
        """

        if self.status_provider is not None:
            return self.status_provider

        if self.connection_manager is None:
            raise RuntimeError("Router connection manager is unavailable.")

        connection = self.connection_manager.connection

        if connection is None:
            raise RuntimeError("Router is not connected.")

        if self.firmware_identity is None:
            raise RuntimeError("Router firmware has not been detected.")

        self.status_provider = (
            ProviderRegistry()
            .get_provider(
                self.firmware_identity,
                connection,
            )
        )

        return self.status_provider

    def status(self):
        """
        Return complete router status.

        Individual metrics may fail without
        preventing other status information
        from being returned.
        """
        from router_controller.router_comms.router.status import Status
        
        provider = self.firmware_status_provider

        errors = []

        system = None
        memory = None
        storage = None
        temperature = None

        try:
            system = provider.get_system_status()
        except Exception as exc:
            errors.append(f"System status unavailable: {exc}")

        try:
            memory = provider.get_memory_status()
        except Exception as exc:
            errors.append(f"Memory status unavailable: {exc}")

        try:
            storage = provider.get_storage_status()
        except Exception as exc:
            errors.append(f"Storage status unavailable: {exc}")

        try:
            temperature = provider.get_temperature_status()
        except Exception as exc:
            errors.append(f"Temperature unavailable: {exc}")

        return Status(
            system=system,
            memory=memory,
            storage=storage,
            temperature=temperature,
            errors=tuple(errors),
        )