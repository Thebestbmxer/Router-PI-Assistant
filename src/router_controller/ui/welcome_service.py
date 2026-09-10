from dataclasses import dataclass

@dataclass(frozen=True)
class WelcomeStatus:
    router_known: bool
    ssh_key_present: bool
    ready: bool

class WelcomeService:
    def __init__(
        self,
        router_repository,
        key_manager,
    ):
        self.router_repository = router_repository
        self.key_manager = key_manager

    def get_status(self) -> WelcomeStatus:
        router_state = self.router_repository.load()

        router_known = router_state is not None

        try:
            self.key_manager.load_key_pair()
            ssh_key_present = True
        except FileNotFoundError:
            ssh_key_present = False

        return WelcomeStatus(
            router_known=router_known,
            ssh_key_present=ssh_key_present,
            ready=(
                router_known
                and ssh_key_present
            ),
        )
