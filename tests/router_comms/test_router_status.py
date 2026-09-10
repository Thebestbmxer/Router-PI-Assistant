from router_controller.router_comms.discovery.router_discovery import RouterCandidate
from router_controller.router_comms.router.identity import RouterIdentity
from router_controller.router_comms.router.router import Router
from router_controller.router_comms.router.status import (
    MemoryStatus,
    StorageStatus,
    SystemStatus,
    Status,
)

class FakeStatusProvider:
    def get_system_status(self):
        return SystemStatus(
            hostname="test-router",
            model="test-model",
            architecture="arm",
            target_platform="test",
            firmware_version="1.0",
            kernel_version="5.0",
            local_time=None,
            uptime="100",
            load_average=(0.1, 0.2, 0.3),
        )

    def get_memory_status(self):
        return MemoryStatus(
            total=100,
            available=50,
            used=50,
            cached=None,
            swap_free=None,
        )

    def get_storage_status(self):
        return StorageStatus(
            disk_total=1000,
            disk_available=500,
            disk_used=500,
            temporary_total=None,
            temporary_available=None,
            temporary_used=None,
        )

    def get_temperature_status(self):
        return 42.0

def test_router_returns_status():
    router = Router(
        identity=RouterIdentity(mac_address="AA:BB:CC:DD:EE:FF"),
        candidate=RouterCandidate(
            address="192.168.1.1",
            ssh_port=22,
        ),
    )

    router.status_provider = FakeStatusProvider()
    status = router.status()

    assert isinstance(status, Status)

    assert status.system.hostname == "test-router"
    assert status.memory.used == 50
    assert status.storage.disk_total == 1000
    assert status.temperature == 42.0

class PartialFailureStatusProvider:
    def get_system_status(self):
        raise RuntimeError("system unavailable")

    def get_memory_status(self):
        return MemoryStatus(
            total=100,
            available=75,
            used=25,
            cached=None,
            swap_free=None,
        )

    def get_storage_status(self):
        return None

    def get_temperature_status(self):
        raise RuntimeError("temperature unavailable")

def test_router_returns_partial_status_on_provider_failure():
    router = Router(
        identity=RouterIdentity(mac_address="AA:BB:CC:DD:EE:FF"),
        candidate=RouterCandidate(
            address="192.168.1.1",
            ssh_port=22,
        ),
    )

    router.status_provider = PartialFailureStatusProvider()
    status = router.status()

    assert status.system is None
    assert status.memory.used == 25
    assert status.storage is None
    assert status.temperature is None
    assert len(status.errors) == 2