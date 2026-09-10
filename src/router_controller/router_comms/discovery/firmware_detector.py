from dataclasses import dataclass


@dataclass(frozen=True)
class FirmwareIdentity:
    name: str
    version: str | None = None
    target: str | None = None


class FirmwareDetector:
    """
    Identifies router firmware using router-side information.
    """

    def __init__(self, connection):
        self.connection = connection

    def detect(self) -> FirmwareIdentity:

        release = self._read_openwrt_release()

        if release:
            return FirmwareIdentity(
                name="openwrt",
                version=release.get(
                    "DISTRIB_RELEASE"
                ),
                target=release.get(
                    "DISTRIB_TARGET"
                ),
            )

        return FirmwareIdentity(
            name="unknown"
        )


    def _read_openwrt_release(self):

        stdout, stderr, code = (
            self.connection.execute(
                "cat /etc/openwrt_release"
            )
        )

        if code != 0:
            return None

        values = {}

        for line in stdout.splitlines():

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            values[key.strip()] = (
                value.strip()
                .strip("'")
            )

        if values.get(
            "DISTRIB_ID"
        ) != "OpenWrt":

            return None

        return values
