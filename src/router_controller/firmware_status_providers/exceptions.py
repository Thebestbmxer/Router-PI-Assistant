
class FirmwareStatusError(Exception):
    """
    Base exception for firmware status failures.
    """

class StatusCommandError(FirmwareStatusError):
    """
    A router command failed while collecting status.
    """

class StatusUnavailableError(FirmwareStatusError):
    """
    Required status information could not be obtained.
    """
