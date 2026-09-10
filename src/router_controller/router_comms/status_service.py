from router_controller.router_comms.router.status import Status

class RouterStatusService:
    """
    GUI-facing router status service.
    Provides firmware-neutral router status.
    """
    def __init__(self, router):
        self.router = router

    def get_status(self) -> Status:
        """
        Return complete router status.
        """
        return self.router.status()

    def get_system_status(self):
        return self.get_status().system

    def get_memory_status(self):
        return self.get_status().memory

    def get_storage_status(self):
        return self.get_status().storage

    def get_temperature_status(self):
        return self.get_status().temperature
