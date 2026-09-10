from dataclasses import dataclass


@dataclass
class WelcomeStatus:
    router_found: bool = False
    mac_known: bool = False
    ssh_key_present: bool = False
    ssh_key_valid: bool = False
    ready: bool = False

    address: str | None = None
    ssh_port: int | None = None
    mac_address: str | None = None

    message: str = ""
