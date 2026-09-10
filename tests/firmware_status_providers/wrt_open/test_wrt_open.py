from router_controller.firmware_status_providers.wrt_open.provider import (
    WrtOpenStatusProvider,
)


class FakeConnection:

    def execute(self, command):

        responses = {

            "cat /etc/openwrt_release":
            """
            DISTRIB_RELEASE='22.03.2'
            DISTRIB_TARGET='ath79/tiny'
            DISTRIB_ARCH='mips_24kc'
            """,

            "cat /proc/sys/kernel/hostname":
            "OpenWrt",

            "uname -r":
            "5.10.146",

            "cat /proc/loadavg":
            "0.32 0.09 0.03 1/37",

            "cat /proc/meminfo":
            """
            MemTotal: 28032 kB
            MemAvailable: 11764 kB
            Cached: 3140 kB
            SwapFree: 12796 kB
            """,
        }

        return (
            responses.get(command, ""),
            "",
            0,
        )


def test_openwrt_system_status():

    provider = OpenWrtStatusProvider(
        FakeConnection()
    )

    status = provider.get_system_status()

    assert (
        status.firmware_version
        == "22.03.2"
    )

    assert (
        status.target_platform
        == "ath79/tiny"
    )


def test_openwrt_memory_status():

    provider = OpenWrtStatusProvider(
        FakeConnection()
    )

    memory = provider.get_memory_status()

    assert memory.total == 28032 * 1024
    assert memory.swap_free == 12796 * 1024
