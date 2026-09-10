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
