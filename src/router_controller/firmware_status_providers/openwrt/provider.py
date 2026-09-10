from router_controller.firmware_status_providers.provider import (
    StatusProvider,
)

from router_controller.router_comms.router.status import (
    MemoryStatus,
    StorageStatus,
    SystemStatus
)

from . import commands
from .parsers import (
    parse_load_average,
    parse_meminfo,
    parse_release,
    parse_storage
)


class OpenWrtStatusProvider(StatusProvider):
    def __init__(self, connection):
        self.connection = connection

    def _run(self, command: str) -> str | None:

        stdout, stderr, code = (
            self.connection.execute(command)
        )

        if code != 0:
            return None

        return stdout.strip()

    def get_system_status(self) -> SystemStatus:
        release = parse_release(
            self._run(commands.SYSTEM_RELEASE)
            or ""
        )

        return SystemStatus(
            hostname=(
                self._run(commands.HOSTNAME)
                or "unknown"
            ),

            model=None,

            architecture=(release.get("DISTRIB_ARCH")),
            target_platform=(release.get("DISTRIB_TARGET")),
            firmware_version=(release.get("DISTRIB_RELEASE")),
            kernel_version=(self._run(commands.KERNEL)),

            local_time=None,
            uptime=(self._run(commands.UPTIME)),
            load_average=(
                parse_load_average(
                    self._run(commands.LOAD_AVERAGE)
                    or ""
                )
            ),
        )


    def get_memory_status(self) -> MemoryStatus:
        memory = parse_meminfo(
            self._run(commands.MEMORY)
            or ""
        )

        total = memory.get("MemTotal")
        available = memory.get("MemAvailable")

        return MemoryStatus(
            total=total,
            available=available,

            used=(
                total - available
                if total is not None
                and available is not None
                else None
            ),

            cached=memory.get("Cached"),
            swap_free=memory.get("SwapFree"),
        )


    def get_storage_status(self):
        storage = parse_storage(
            self._run(commands.STORAGE)
            or ""
        )

        if not storage:
            return None

        return StorageStatus(
            disk_total=storage.get("total"),
            disk_available=storage.get("available"),
            disk_used=storage.get("used"),

            temporary_total=None,
            temporary_available=None,
            temporary_used=None,
        )

    def get_temperature_status(self):
        value = self._run(commands.TEMPERATURE)

        if value is None:
            return None

        try:
            return int(value) / 1000

        except ValueError:
            return None
