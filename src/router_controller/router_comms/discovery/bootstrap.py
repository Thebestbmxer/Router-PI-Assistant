"""Initial communication with a freshly reset router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import paramiko
import base64
import hashlib

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
)


DEFAULT_USERNAME = "root"
DEFAULT_PASSWORDS: tuple[str, ...] = (
    "",
    "password",
)


@dataclass(frozen=True)
class BootstrapCredentials:
    """Credentials successfully used during bootstrap."""

    username: str
    password: str
    ssh_host_key_fingerprint: str

def host_key_fingerprint(key: paramiko.PKey) -> str:
    """Return an OpenSSH-style SHA256 fingerprint for an SSH host key."""
    digest = hashlib.sha256(key.asbytes()).digest()
    encoded = base64.b64encode(digest).decode("ascii").rstrip("=")
    return f"SHA256:{encoded}"

class RouterBootstrap:
    """Establish initial communication with a freshly reset router."""

    def __init__(
        self,
        candidate: RouterCandidate,
        username: str = DEFAULT_USERNAME,
        passwords: Sequence[str] = DEFAULT_PASSWORDS,
        timeout: float = 5.0,
    ) -> None:
        self.candidate = candidate
        self.username = username
        self.passwords = tuple(passwords)
        self.timeout = timeout

    def connect(self) -> tuple[paramiko.SSHClient, BootstrapCredentials]:
        """Connect using the configured bootstrap credentials."""

        last_error: Exception | None = None

        for password in self.passwords:
            try:
                if password == "":
                    client = self._connect_without_password()
                else:
                    client = self._connect_with_password(password)

                credentials = BootstrapCredentials(
                    username=self.username,
                    password=password,
                )

                return client, credentials

            except paramiko.AuthenticationException as exc:
                last_error = exc

            except (
                paramiko.SSHException,
                OSError,
            ) as exc:
                raise InitialCommunicationError(
                    f"Unable to establish SSH communication with "
                    f"{self.candidate.address}:{self.candidate.ssh_port}."
                ) from exc

        transport = client.get_transport()

        if transport is None:
            raise InitialCommunicationError(
                "Bootstrap SSH transport was not established."
            )

        host_key = transport.get_remote_server_key()

        if host_key is None:
            raise InitialCommunicationError(
                "Bootstrap SSH host key could not be determined."
            )

        fingerprint = host_key_fingerprint(host_key)

        raise AuthenticationError(
            f"Bootstrap authentication failed for "
            f"{self.username}@{self.candidate.address}."
        ) from last_error

    
        return client, BootstrapCredentials(
            username=self.username,
            password=password,
            ssh_host_key_fingerprint=fingerprint,
        )

    def _connect_without_password(self) -> paramiko.SSHClient:
        """Connect using SSH none authentication.

        OpenWrt's Dropbear server can accept a root account with no
        password through SSH 'none' authentication. This is different
        from password authentication with an empty password.
        """

        client = self._create_client()

        transport = paramiko.Transport(
            (self.candidate.address, self.candidate.ssh_port)
        )

        try:
            transport.start_client(timeout=self.timeout)
            transport.auth_none(self.username)

            if not transport.is_authenticated():
                raise paramiko.AuthenticationException(
                    "SSH none authentication failed."
                )

            # SSHClient normally owns the transport created by
            # SSHClient.connect(). Here we created the transport
            # explicitly because Paramiko's password="" path does not
            # perform SSH none authentication.
            client._transport = transport

            return client

        except Exception:
            transport.close()
            raise

    def _connect_with_password(
        self,
        password: str,
    ) -> paramiko.SSHClient:
        """Connect using normal SSH password authentication."""

        client = self._create_client()

        try:
            client.connect(
                hostname=self.candidate.address,
                port=self.candidate.ssh_port,
                username=self.username,
                password=password,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False,
            )

            return client

        except Exception:
            client.close()
            raise

    @staticmethod
    def _create_client() -> paramiko.SSHClient:
        """Create an SSH client for bootstrap communication."""

        client = paramiko.SSHClient()

        # Bootstrap host-key handling is intentionally separate from
        # the permanent SSH connection. The permanent connection will
        # require an explicitly trusted host key.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        return client

    @property
    def host_key_fingerprint(self) -> str | None:
        """Return the fingerprint of the connected router host key."""
        transport = getattr(self, "_transport", None)

        if transport is None:
            return None

        host_key = transport.get_remote_server_key()

        if host_key is None:
            return None

        return host_key_fingerprint(host_key)
