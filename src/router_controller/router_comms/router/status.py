from dataclasses import dataclass


@dataclass(frozen=True)
class SystemStatus:
    hostname: str
    model: str | None
    architecture: str | None
    target_platform: str | None
    firmware_version: str | None
    kernel_version: str | None
    local_time: str | None
    uptime: str | None
    load_average: tuple[float, float, float] | None


@dataclass(frozen=True)
class MemoryStatus:
    total: int | None
    available: int | None
    used: int | None
    cached: int | None
    swap_free: int | None


@dataclass(frozen=True)
class StorageStatus:
    disk_total: int | None
    disk_available: int | None
    disk_used: int | None
    temporary_total: int | None
    temporary_available: int | None
    temporary_used: int | None


@dataclass(frozen=True)
class Status:
    system: RouterSystemStatus
    memory: RouterMemoryStatus
    storage: RouterStorageStatus
    temperature: float | None
