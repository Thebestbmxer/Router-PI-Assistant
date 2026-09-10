from typing import Protocol

from router_controller.router_comms.router.status import (
    MemoryStatus,
    StorageStatus,
    SystemStatus,
)


class StatusProvider(Protocol):
    """
    Firmware-neutral status provider interface.

    Implementations translate firmware-specific
    router information into common application models.
    """

    def get_system_status(self) -> SystemStatus:
        """
        Return system information.
        """
        ...

    def get_memory_status(self) -> MemoryStatus:
        """
        Return memory information.
        """
        ...

    def get_storage_status(self) -> StorageStatus | None:
        """
        Return storage information when supported.
        """
        ...

    def get_temperature_status(self) -> float | None:
        """
        Return temperature when supported.
        """
        ...
