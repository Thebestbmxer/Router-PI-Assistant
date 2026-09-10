from router_controller.firmware_status_providers.provider import (
    StatusProvider,
)
from router_controller.firmware_status_providers.exceptions import (
    StatusCommandError,
)
from router_controller.router_comms.router.status import (
    MemoryStatus,
    StorageStatus,
    SystemStatus,
)


class WrtOpenStatusProvider(StatusProvider):
    """
    Implementation of router status collection.
    """

    def __init__(self, connection) -> None:
        self.connection = connection

    def _execute(self, command: str) -> str:
        """
        Execute a router command and return stdout.
        """

        stdout, stderr, exit_status = self.connection.execute(
            command
        )

        if exit_status != 0:
            raise StatusCommandError(
                f"Command failed: {command}: {stderr}"
            )

        return stdout.strip()

    def get_system_status(self) -> SystemStatus:
        release = self._parse_release()

        hostname = self._safe_command(
            "cat /proc/sys/kernel/hostname"
        )

        kernel = self._safe_command(
            "uname -r"
        )

        architecture = self._safe_command(
            "uname -m"
        )

        uptime = self._safe_command(
            "cat /proc/uptime"
        )

        load = self._parse_load_average(
            self._safe_command(
                "cat /proc/loadavg"
            )
        )

        return SystemStatus(
            hostname=hostname or "unknown",
            model=None,
            architecture=(
                release.get("DISTRIB_ARCH")
                or architecture
            ),
            target_platform=release.get(
                "DISTRIB_TARGET"
            ),
            firmware_version=release.get(
                "DISTRIB_RELEASE"
            ),
            kernel_version=kernel,
            local_time=None,
            uptime=uptime,
            load_average=load,
        )

    def get_memory_status(self) -> MemoryStatus:
        data = self._parse_meminfo(
            self._execute(
                "cat /proc/meminfo"
            )
        )

        total = data.get("MemTotal")
        available = data.get("MemAvailable")

        used = None

        if total is not None and available is not None:
            used = total - available

        return MemoryStatus(
            total=total,
            available=available,
            used=used,
            cached=data.get("Cached"),
            swap_free=data.get("SwapFree"),
        )

    def get_storage_status(self) -> StorageStatus:
        return StorageStatus(
            disk_total=None,
            disk_available=None,
            disk_used=None,
            temporary_total=None,
            temporary_available=None,
            temporary_used=None,
        )

    def get_temperature_status(self) -> float | None:
        value = self._safe_command(
            "cat /sys/class/thermal/thermal_zone0/temp"
        )

        if not value:
            return None

        try:
            return int(value) / 1000
        except ValueError:
            return None

    def _parse_release(self) -> dict[str, str]:
        output = self._safe_command(
            "cat /etc/openwrt_release"
        )

        result = {}

        for line in output.splitlines():
            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            result[key.strip()] = (
                value.strip()
                .strip("'")
            )

        return result

    def _parse_meminfo(
        self,
        output: str,
    ) -> dict[str, int]:

        result = {}

        for line in output.splitlines():
            if ":" not in line:
                continue

            key, value = line.split(
                ":",
                1,
            )

            value = value.strip()

            if value.endswith(" kB"):
                value = value[:-3]

            try:
                result[key] = int(value) * 1024
            except ValueError:
                continue

        return result

    def _parse_load_average(
        self,
        output: str,
    ) -> tuple[float, float, float] | None:

        parts = output.split()

        if len(parts) < 3:
            return None

        try:
            return (
                float(parts[0]),
                float(parts[1]),
                float(parts[2]),
            )

        except ValueError:
            return None

    def _safe_command(
        self,
        command: str,
    ) -> str | None:

        try:
            return self._execute(command)

        except StatusCommandError:
            return None
