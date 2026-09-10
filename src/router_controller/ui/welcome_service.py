from .welcome_status import WelcomeStatus


class WelcomeService:
    def __init__(
        self,
        router_repository,
        key_manager,
    ):
        self.router_repository = router_repository
        self.key_manager = key_manager

    def get_status(self):
        status = WelcomeStatus()

        try:
            router_state = self.router_repository.load()
        except FileNotFoundError:
            status.message = "No trusted router configured."
            return status


        if router_state is None:
            status.message = "No trusted router configured."
            return status

        status.mac_known = True
        status.mac_address = router_state.mac_address
        status.address = router_state.ip_address
        status.ssh_port = router_state.ssh_port

        status.ssh_key_present = self.key_manager.exists()
        status.ssh_key_valid = status.ssh_key_present
        status.ready = (
            status.mac_known
            and status.ssh_key_valid
        )

        if status.ready:
            status.message = "Router trusted and ready."
        else:
            status.message = "Router requires SSH provisioning."

        return status
