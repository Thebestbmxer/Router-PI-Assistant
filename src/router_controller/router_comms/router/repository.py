"""Persistence for known router state."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from router_controller.router_comms.router.state import RouterState


class RouterStateRepository:
    """Persist the currently known router."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def save(self, state: RouterState) -> None:
        """Persist router state."""

        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.path.write_text(
            json.dumps(
                asdict(state),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def load(self) -> RouterState | None:
        """Load persisted router state."""

        if not self.path.exists():
            return None

        data = json.loads(
            self.path.read_text(encoding="utf-8")
        )

        return RouterState(**data)

class RouterRepository:
    """Persisted router state lookup."""

    def __init__(self, database):
        self.database = database

    def find_by_mac(
        self,
        mac_address: str,
    ) -> RouterState | None:
        """Return persisted router state for a MAC address."""

        if not mac_address:
            return None

        # Implement using the application's existing database layer.
        #
        # This method should return RouterState when the router is known
        # and None when it is not known.
        raise NotImplementedError
