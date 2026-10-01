from pathlib import Path

from flask import current_app
from jinja2 import Environment, FileSystemLoader


def render_layout_template(
    template_name: str,
    **context,
) -> str:
    """Render a template from the active layout."""

    manager = current_app.extensions[
        "layout_manager"
    ]

    layout = manager.active()

    if layout is None:
        raise RuntimeError(
            "No active layout is available."
        )

    template_path = (layout.path / "templates")

    environment = Environment(
        loader=FileSystemLoader(
            str(template_path)
        )
    )

    template = environment.get_template(template_name)

    return template.render(**context)
