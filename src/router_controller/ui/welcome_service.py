from dataclasses import dataclass


@dataclass(frozen=True)
class WelcomeStatus:
    router_known: bool
    ssh_key_valid: bool
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
        state = self.router_repository.load()

        if state is None:
            return WelcomeStatus(
                router_known=False,
                ssh_key_valid=False,
                ready=False,
            )

        try:
            self.key_manager.load_key_pair()

        except FileNotFoundError:
            return WelcomeStatus(
                router_known=True,
                ssh_key_valid=False,
                ready=False,
            )

        return WelcomeStatus(
            router_known=True,
            ssh_key_valid=True,
            ready=True,
        )
