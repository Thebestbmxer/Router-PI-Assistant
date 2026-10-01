from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class LayoutDefinition:
    id: str
    name: str
    version: str
    description: str
    path: Path
    '''
    template_path: Path
    stylesheet_path: Path
    tabs_path: Path

    layout_type: str
    tab_position: str
    density: str
    theme_mode: str
    accent: str
    '''