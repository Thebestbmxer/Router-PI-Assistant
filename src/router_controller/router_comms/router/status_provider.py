from typing import Protocol

from router_controller.router_comms.router.status import Status


class RouterStatusProvider(Protocol):
    def get_status(self) -> Status:
        """Collect the current router status."""
        ...
