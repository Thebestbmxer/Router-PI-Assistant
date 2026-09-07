"""Construction of router communication services."""

from __future__ import annotations

from router_controller.config import Config
from router_controller.router_comms.discovery.bootstrap        import RouterBootstrap
from router_controller.router_comms.discovery.router_discovery import RouterDiscovery
from router_controller.router_comms.provisioner import RouterProvisioner
from router_controller.router_comms.ssh.key_installer import RouterKeyInstaller
from router_controller.router_comms.ssh.keys          import SSHKeyManager
from router_controller.router_comms.ssh.connection    import RouterConnection
from router_controller.router_comms.router.repository import RouterStateRepository


def create_router_provisioner(
    config_class: type[Config] = Config,
) -> RouterProvisioner:

    key_manager = SSHKeyManager(
        config_class.get_ssh_key_directory()
    )

    discovery = RouterDiscovery(
        ssh_port=config_class.ROUTER_SSH_PORT,
        timeout=config_class.ROUTER_SSH_TIMEOUT,
    )

    router_repository = RouterStateRepository(
        config_class.get_database_path()
    )

    return RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=lambda candidate: RouterBootstrap(
            candidate=candidate,
            username=config_class.ROUTER_SSH_USER,
            timeout=config_class.ROUTER_SSH_TIMEOUT,
        ),
        installer_factory=lambda client: RouterKeyInstaller(client),
        connection_factory=lambda candidate, key_pair: RouterConnection(
            candidate=candidate,
            key_pair=key_pair,
            config=config,
        ),
        router_repository=router_repository,
    )
