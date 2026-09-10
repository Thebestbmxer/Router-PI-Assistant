from router_controller.firmware_status_providers.openwrt.provider import (
    OpenWrtStatusProvider,
)


class UnsupportedFirmwareProvider:

    def __init__(self, connection):
        self.connection = connection


    def get_system_status(self):
        raise RuntimeError(
            "Unsupported firmware"
        )


class ProviderRegistry:
    """
    Maps firmware identity to providers.
    """

    def __init__(self):
        self.providers = {
            "openwrt": OpenWrtStatusProvider,
        }


    def get_provider(
        self,
        identity,
        connection,
    ):

        provider = self.providers.get(
            identity.name
        )

        if provider is None:
            return UnsupportedFirmwareProvider(
                connection
            )

        return provider(
            connection
        )
