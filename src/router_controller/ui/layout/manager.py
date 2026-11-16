import json

from pathlib import Path
from .definition import LayoutDefinition

class LayoutManager:

    def __init__(self, layouts_path: Path):
        self.layouts_path = layouts_path

        self.registry_path = (
            layouts_path /
            "active_layouts.json"
        )

        self.layouts = {}
        self.active_layout_id = "default"
        self.tabs = []
        self.load()

    def load(self):
        with self.registry_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            registry = json.load(file)

        self.active_layout_id = registry.get(
            "active_layout",
            "default",
        )

        enabled_layouts = registry.get(
                "enabled",
                [],
            )

        for layout_id in enabled_layouts:
            self._load_layout(
                layout_id,
                load_tabs=False,
            )

        if self.active_layout_id not in self.layouts:
            raise RuntimeError(
                f"Active layout "
                f"'{self.active_layout_id}' "
                f"is not available."
            )

        active_layout = self.active()
        self._load_tabs(active_layout.path)

    def _load_layout(
        self,
        layout_id: str,
        load_tabs: bool = False
        ):
        layout_path = (self.layouts_path / layout_id)
        definition_path = (layout_path / "layout.json")

        if not definition_path.exists():
            raise FileNotFoundError(
                f"Layout definition not found: {definition_path}"
            )

        with definition_path.open(
            "r",
            encoding="utf-8",
        ) as file: 
            data = json.load(file)

        layout = LayoutDefinition(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "0.0.0"),
            description=data.get("description", ""),
            path=layout_path,
        )

        self.layouts[layout.id] = layout
        if load_tabs: self._load_tabs(layout_path)

    def _load_tabs(self, layout_path: Path):
        """Load navigation tabs for a layout."""

        tabs_path = layout_path / "tabs.json"

        if not tabs_path.is_file():
            raise FileNotFoundError(
                f"Tabs configuration not found: {tabs_path}"
            )

        with tabs_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.tabs = data.get("tabs", [])

    def active(self):
        """Return the currently active layout."""
        return self.layouts.get(self.active_layout_id)

    def available(self):
        """Return all enabled layouts."""
        return list(self.layouts.values())

    def set_active(self, layout_id: str):
        """Switch to an enabled layout."""
        layout = self.layouts.get(layout_id)

        if layout is None:
            raise ValueError(
                f"Layout '{layout_id}' is not available."
            )

        tabs_path = layout.path / "tabs.json"

        if not tabs_path.is_file():
            raise FileNotFoundError(
                f"Tabs configuration not found: {tabs_path}"
            )

        with tabs_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        tabs = data.get("tabs", [])

        registry = {
            "active_layout": layout_id,
            "enabled": list(self.layouts.keys()),
        }

        with self.registry_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                registry,
                file,
                indent=4,
            )
            file.write("\n")

        self.active_layout_id = layout_id
        self.tabs = tabs

        return layout

    def template_path(
        self,
        template_name: str,
        ) -> Path:
        """Return the path to a template in the active layout."""

        layout = self.active()

        if layout is None:
            raise RuntimeError(
                f"Active layout "
                f"'{self.active_layout_id}' "
                f"is not loaded."
            )

        template_path = (
            layout.path
            / "templates"
            / template_name
        )

        if not template_path.is_file():
            raise FileNotFoundError(
                f"Template not found: "
                f"{template_path}"
            )

        return template_path