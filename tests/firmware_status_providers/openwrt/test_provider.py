from router_controller.firmware_status_providers.openwrt.provider import (
    OpenWrtStatusProvider,
)

class FakeConnection:
    def execute(self, command):
        if command == "df -k":
            return (
                """
Filesystem 1024-blocks Used Available Mounted on
/dev/root 15360 9000 6360 /
""",
                "",
                0,
            )

        return (
            "",
            "",
            0,
        )

def test_storage_status():
    provider = OpenWrtStatusProvider(FakeConnection())
    result = (provider.get_storage_status())

    assert result.total == 15360 * 1024
    assert result.used == 9000 * 1024
