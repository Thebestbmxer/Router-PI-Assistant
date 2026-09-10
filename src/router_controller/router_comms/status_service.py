class RouterStatusService:
    def __init__(self, router):
        self.router = router

    def get_system_status(self):
        return (
            self.router
            .status_provider
            .get_system_status()
        )

    def get_memory_status(self):
        return (
            self.router
            .status_provider
            .get_memory_status()
        )

    def get_storage_status(self):
        return (
            self.router
            .status_provider
            .get_storage_status()
        )

    def get_temperature_status(self):
        return (
            self.router
            .status_provider
            .get_temperature_status()
        )
