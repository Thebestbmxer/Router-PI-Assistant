from router_controller.router_comms.router.status import Status

class BrokenProvider:
    def get_system_status(self):
        raise RuntimeError("system failed")

    def get_memory_status(self):
        return "memory"

    def get_storage_status(self):
        return None

    def get_temperature_status(self):
        raise RuntimeError("temperature failed")

def test_router_status_returns_partial_results():
    provider = BrokenProvider()

    result = Status(
        system=None,
        memory=provider.get_memory_status(),
        storage=None,
        temperature=None,
        errors=(
            "System failed",
            "Temperature failed",
        ),
    )

    assert result.memory == "memory"
    assert result.system is None