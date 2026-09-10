import pytest

from router_controller.app import create_app


@pytest.fixture
def client(tmp_path):
    class TestConfig:
        TESTING = True
        DATA_DIR = tmp_path
        DATABASE_PATH = tmp_path / "controller.db"

    app = create_app(TestConfig)

    return app.test_client()
