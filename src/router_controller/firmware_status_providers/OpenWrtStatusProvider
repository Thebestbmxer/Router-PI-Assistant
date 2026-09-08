class OpenWrtStatusProvider:
    def __init__(self, connection: RouterConnection) -> None:
        self.connection = connection

    def get_status(self) -> RouterStatus:
        system = self._get_system()
        memory = self._get_memory()
        storage = self._get_storage()
        temperature = self._get_temperature()

        return RouterStatus(
            system=system,
            memory=memory,
            storage=storage,
            temperature=temperature,
        )
