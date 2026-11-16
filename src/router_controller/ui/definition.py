from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class LayoutDefinition:
    id: str
    name: str
    version: str
    description: str
    path: Path
