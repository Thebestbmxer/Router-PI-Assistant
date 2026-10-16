
"""Tests for the router status UI API."""

from dataclasses import dataclass

import pytest
from flask import Flask

from router_controller.ui.status import register_status_routes


@dataclass
class FakeStatus:
    system: dict | None = None
    memory: dict | None = None
    storage: dict | None = None
    temperature: float | None = None
    errors: list | None = None


@dataclass
class FakeCandidate:
    address: str = "192.168.1.1"
    ssh_port: int = 22


@dataclass
class FakeIdentity:
    mac_address: str = "AA:BB:CC:DD:EE:FF"


@dataclass
class FakeFirmware:
    name: str = "OpenWrt"


class FakeRouter:
    def __init__(self, *, connected=True, status=None, error=None):
        self.connected = connected
        self.candidate = FakeCandidate()
        self.identity = FakeIdentity()
        self.firmware_identity = FakeFirmware()
        self._status = status or FakeStatus(
            system={"hostname": "test-router"},
            memory={"total": 128},
            storage=None,
            temperature=None,
            errors=[],
        )
        self._error = error

    def status(self):
        if self._error:
            raise self._error
        return self._status


@pytest.fixture
def app():
    app = Flask(__name__)
    register_status_routes(app)
    app.config.update(TESTING=True)
    return app


def test_status_api_without_router_returns_503(app):
    response = app.test_client().get("/api/router/status")

    assert response.status_code == 503
    assert response.json["configured"] is False
    assert response.json["connected"] is False
    assert response.json["errors"] == []


def test_status_api_with_disconnected_router_returns_503(app):
    app.extensions["router"] = FakeRouter(connected=False)

    response = app.test_client().get("/api/router/status")

    assert response.status_code == 503
    assert response.json["configured"] is True
    assert response.json["connected"] is False


def test_status_api_returns_router_metadata_and_metrics(app):
    app.extensions["router"] = FakeRouter()

    response = app.test_client().get("/api/router/status")

    assert response.status_code == 200
    data = response.json

    assert data["configured"] is True
    assert data["connected"] is True
    assert data["address"] == "192.168.1.1"
    assert data["ssh_port"] == 22
    assert data["mac_address"] == "AA:BB:CC:DD:EE:FF"
    assert data["firmware"] == "OpenWrt"
    assert data["system"]["hostname"] == "test-router"
    assert data["memory"]["total"] == 128
    assert data["errors"] == []


def test_status_api_preserves_connection_metadata(app):
    app.extensions["router"] = FakeRouter(
        status=FakeStatus(
            system={"hostname": "test-router"},
            errors=[],
        )
    )

    response = app.test_client().get("/api/router/status")

    assert response.status_code == 200
    assert response.json["connected"] is True
    assert response.json["address"] == "192.168.1.1"


def test_status_api_reports_collection_failure(app):
    app.extensions["router"] = FakeRouter(
        error=RuntimeError("private connection details")
    )

    response = app.test_client().get("/api/router/status")

    assert response.status_code == 200
    assert response.json["connected"] is True
    assert response.json["system"] is None
    assert response.json["errors"] == [
        "Router status collection failed."
    ]
    assert "private connection details" not in response.get_data(
        as_text=True
    )


def test_status_api_reports_partial_metric_failures(app):
    app.extensions["router"] = FakeRouter(
        status=FakeStatus(
            system={"hostname": "test-router"},
            errors=["Temperature sensor unavailable."],
        )
    )

    response = app.test_client().get("/api/router/status")

    assert response.status_code == 200
    assert response.json["connected"] is True
    assert response.json["system"]["hostname"] == "test-router"
    assert response.json["errors"] == [
        "Temperature sensor unavailable."
    ]
    assert "some status information is unavailable" in (
        response.json["message"]
    )
