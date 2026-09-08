from typing import Protocol

from router_controller.router_comms.router.status import Status


class StatusProvider(Protocol):
    def get_status(self) -> Status:
        """Collect the current status."""
        ...
