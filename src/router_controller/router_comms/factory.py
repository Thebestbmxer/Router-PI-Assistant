"""Construction of router communication services."""

from __future__ import annotations
from dataclasses import dataclass

from router_controller.config import Config
from router_controller.router_comms.discovery.bootstrap        import RouterBootstrap
from router_controller.router_comms.discovery.router_discovery import RouterDiscovery
from router_controller.router_comms.provisioner import RouterProvisioner
from router_controller.router_comms.ssh.key_installer import RouterKeyInstaller
from router_controller.router_comms.ssh.keys          import SSHKeyManager
from router_controller.router_comms.ssh.connection    import RouterConnection
from router_controller.router_comms.router.repository import RouterStateRepository

@dataclass
class RouterServices:
    provisioner: RouterProvisioner
    key_manager: SSHKeyManager
    router_repository: RouterStateRepository

def create_router_services(
    config_class: type[Config] = Config,
) -> RouterServices:

    key_manager = SSHKeyManager(config_class.get_ssh_key_directory())
    router_repository = RouterStateRepository(config_class.get_router_state_path())

    provisioner = RouterProvisioner(
        key_manager=key_manager,
        discovery=RouterDiscovery(
            ssh_port=config_class.ROUTER_SSH_PORT,
            timeout=config_class.ROUTER_SSH_TIMEOUT,
        ),
        bootstrap_factory=lambda candidate: RouterBootstrap(
            candidate=candidate,
            username=config_class.ROUTER_SSH_USER,
            timeout=config_class.ROUTER_SSH_TIMEOUT,
        ),
        installer_factory=lambda client:
            RouterKeyInstaller(client),

        connection_factory=lambda candidate, key_pair, config:
            RouterConnection(
                candidate=candidate,
                key_pair=key_pair,
                config=config,
            ),

        router_repository=router_repository,
    )

    return RouterServices(
        provisioner=provisioner,
        key_manager=key_manager,
        router_repository=router_repository,
    )

def create_router_provisioner(
    config_class: type[Config] = Config,
) -> RouterProvisioner:

    return create_router_services(config_class).provisioner