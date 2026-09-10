from unittest.mock import Mock
from unittest.mock import MagicMock

import pytest

from router_controller.router_comms.discovery.router_discovery import RouterCandidate
from router_controller.router_comms.discovery.bootstrap import BootstrapCredentials
from router_controller.router_comms.provisioner import RouterProvisioner
from router_controller.router_comms.ssh.connection_manager import RouterConnectionManager
from router_controller.router_comms.ssh.keys import SSHKeyPair
from router_controller.router_comms.router.state import RouterState
from router_controller.router_comms.router.repository import RouterStateRepository

from router_controller.router_comms.discovery.firmware_detector import (
    FirmwareIdentity,
)

@pytest.fixture
def bootstrap_credentials():
    return BootstrapCredentials(
        username="root",
        password="",
        ssh_host_key_fingerprint="SHA256:test-fingerprint",
    )

@pytest.fixture
def router_repository():
    return Mock(spec=RouterStateRepository)


@pytest.fixture
def candidate():
    return RouterCandidate(
        address="192.168.1.1",
        ssh_port=22,
        mac_address="AA:BB:CC:DD:EE:FF",
    )

@pytest.fixture
def key_pair(tmp_path):
    return SSHKeyPair(
        private_key_path=tmp_path / "controller",
        public_key_path=tmp_path / "controller.pub",
        public_key="ssh-rsa AAAATEST controller",
    )

@pytest.fixture
def key_manager():
    return Mock()

@pytest.fixture
def discovery():
    return Mock()

@pytest.fixture
def bootstrap():
    #return Mock(spec=RouterBootstrap)
    return Mock()

@pytest.fixture
def installer():
    return Mock()

@pytest.fixture
def connection():
    connection = Mock()
    connection.connected = True
    return connection

@pytest.fixture
def provisioner(
    key_manager,
    discovery,
    bootstrap,
    installer,
    connection,
    router_repository
):
    bootstrap_factory = Mock(return_value=bootstrap)
    installer_factory = Mock(return_value=installer)
    connection_factory = Mock(return_value=connection)

    instance = RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=bootstrap_factory,
        installer_factory=installer_factory,
        connection_factory=connection_factory,
        router_repository=router_repository,
    )

    instance.bootstrap_factory_mock = bootstrap_factory
    instance.installer_factory_mock = installer_factory
    instance.connection_factory_mock = connection_factory

    return instance


def test_provision_loads_existing_key(
    provisioner,
    key_manager,
    discovery,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
    bootstrap_credentials,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, bootstrap_credentials)

    result = provisioner.provision(candidate)

    assert result.candidate == candidate

    key_manager.load_key_pair.assert_called_once_with()
    key_manager.generate_key_pair.assert_not_called()

    discovery.discover.assert_not_called()
    bootstrap.connect.assert_called_once_with()
    installer.install.assert_called_once_with(key_pair)
    client.close.assert_called_once_with()

    connection.connect.assert_called_once_with()
    
    assert result.connection_manager is not None
    assert result.connection_manager.connection is connection
    #connection.close.assert_called_once_with()


def test_provision_generates_key_when_missing(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.side_effect = FileNotFoundError
    key_manager.generate_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    result = provisioner.provision(candidate)

    assert result.candidate == candidate
    #assert result == candidate

    key_manager.load_key_pair.assert_called_once_with()
    key_manager.generate_key_pair.assert_called_once_with()

    installer.install.assert_called_once_with(key_pair)
    client.close.assert_called_once_with()
    connection.connect.assert_called_once_with()


def test_provision_discovers_when_candidate_not_supplied(
    provisioner,
    key_manager,
    discovery,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair
    discovery.discover.return_value = candidate

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    result = provisioner.provision()

    assert result.candidate == candidate
    #assert result == candidate

    discovery.discover.assert_called_once_with()
    provisioner.bootstrap_factory_mock.assert_called_once_with(candidate)


def test_provision_does_not_discover_when_candidate_supplied(
    provisioner,
    key_manager,
    discovery,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    result = provisioner.provision(candidate)

    assert result.candidate == candidate
    #assert result == candidate
    discovery.discover.assert_not_called()


def test_provision_installs_public_key(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner.provision(candidate)

    provisioner.installer_factory_mock.assert_called_once_with(client)
    installer.install.assert_called_once_with(key_pair)


def test_bootstrap_connection_is_closed_when_install_fails(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    installer.install.side_effect = RuntimeError("install failed")

    with pytest.raises(RuntimeError, match="install failed"):
        provisioner.provision(candidate)

    client.close.assert_called_once_with()
    connection.connect.assert_not_called()


def test_provision_connects_using_controller_key(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner.provision(candidate)
    connection.connect.assert_called_once_with()

def test_provision_closes_bootstrap_before_permanent_connection(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    events = []

    client.close.side_effect = lambda: events.append("bootstrap-close")
    connection.connect.side_effect = lambda: events.append("permanent-connect")

    provisioner.provision(candidate)

    assert events == [
        "bootstrap-close",
        "permanent-connect",
    ]


def test_provision_failure_to_connect_is_propagated(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())
    connection.connect.side_effect = RuntimeError("permanent connection failed")

    with pytest.raises(
        RuntimeError,
        match="permanent connection failed",
    ):
        provisioner.provision(candidate)

    #connection.close.assert_called_once_with()

def test_create_connection_manager(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    connection_factory = MagicMock()

    detector = Mock()
    detector.detect.return_value = FirmwareIdentity(
        name="openwrt"
    )


    provisioner = RouterProvisioner(
        key_manager=MagicMock(),
        discovery=MagicMock(),
        bootstrap_factory=MagicMock(),
        installer_factory=MagicMock(),
        connection_factory=connection_factory,
        router_repository=MagicMock(),
        detector_factory=lambda connection: detector
    )

    manager = provisioner.create_connection_manager(
        candidate,
        key_pair,
    )

    assert isinstance(manager, RouterConnectionManager)
    assert manager.candidate is candidate
    assert manager.key_pair is key_pair
    assert manager.connection_factory is connection_factory

def test_provision_saves_router_state(
    provisioner,
    key_manager,
    bootstrap,
    installer,
    connection,
    candidate,
    key_pair,
    bootstrap_credentials,
    router_repository,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (
        client,
        bootstrap_credentials,
    )

    provisioner.provision(candidate)

    router_repository.save.assert_called_once()

    state = router_repository.save.call_args.args[0]

    assert state.mac_address == candidate.mac_address
    assert state.ssh_host_key == (
        bootstrap_credentials.ssh_host_key_fingerprint
    )
    assert state.ip_address == candidate.address
    assert state.ssh_port == candidate.ssh_port
    assert state.username == bootstrap_credentials.username

    
def test_build_router_state_requires_mac(provisioner):
    candidate = RouterCandidate(
        address="192.168.1.1",
        ssh_port=22,
        mac_address=None,
    )

    with pytest.raises(RuntimeError, match="MAC address"):
        provisioner._build_router_state(
            candidate=candidate,
            username="root",
            fingerprint="SHA256:test",
        )

def test_connect_uses_persisted_host_key(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    state = RouterState(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key="SHA256:trusted-router-key",
        ip_address=candidate.address,
        ssh_port=candidate.ssh_port,
        username="root",
    )

    factory = MagicMock(return_value=connection)

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        state=state,
        connection_factory=factory,
    )

    manager.connect()

    args = factory.call_args.args
    config = args[2]

    assert config.username == "root"
    assert (
        config.expected_host_key_fingerprint
        == "SHA256:trusted-router-key"
    )
