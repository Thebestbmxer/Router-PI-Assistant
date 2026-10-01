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

        self.load()


    def load(self):

        with self.registry_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            registry = json.load(file)


        self.active_layout_id = (
            registry.get(
                "active_layout",
                "default",
            )
        )


        for layout_id in registry.get(
            "enabled",
            [],
        ):

            self._load_layout(
                layout_id
            )


    def _load_layout(
        self,
        layout_id: str,
    ):

        layout_path = (
            self.layouts_path /
            layout_id
        )


        definition_path = (
            layout_path /
            "layout.json"
        )


        if not definition_path.exists():
            return


        with definition_path.open(
            "r",
            encoding="utf-8",
        ) as file: 
            data = json.load(file)

        layout = LayoutDefinition(
            id=data["id"],
            name=data["name"],
            version=data.get(
                "version",
                "0.0.0",
            ),
            description=data.get(
                "description",
                "",
            ),
            path=layout_path,
        )

        self.layouts[
            layout.id
        ] = layout

    def active(self):
        return self.layouts.get(self.active_layout_id)

    def available(self):
        return list(self.layouts.values())