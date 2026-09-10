import pytest

from router_controller.firmware_status_providers.exceptions import StatusCommandError
from router_controller.firmware_status_providers.openwrt.provider import OpenWrtStatusProvider

class FailedConnection:
    def execute(self, command):

        return (
            "",
            "permission denied",
            1,
        )


def test_command_failure_raises_status_error():
    provider = OpenWrtStatusProvider(FailedConnection())

    with pytest.raises(StatusCommandError):
        provider.get_system_status()
