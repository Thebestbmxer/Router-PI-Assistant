from router_controller.router_comms.discovery.firmware_detector import (
    FirmwareDetector,
)


class FakeConnection:

    def execute(self, command):

        return (
            """
            DISTRIB_ID='OpenWrt'
            DISTRIB_RELEASE='22.03.2'
            DISTRIB_TARGET='ath79/tiny'
            """,
            "",
            0,
        )


def test_detect_openwrt():

    detector = FirmwareDetector(
        FakeConnection()
    )

    identity = detector.detect()

    assert identity.name == "openwrt"
    assert identity.version == "22.03.2"
