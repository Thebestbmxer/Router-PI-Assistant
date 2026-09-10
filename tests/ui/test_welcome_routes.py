from router_controller.app import create_app


class FakeWelcomeService:
    def get_status(self):
        class Status:
            router_known = True
            ssh_key_valid = True
            ready = True

        return Status()

def test_router_status_endpoint():
    app = create_app(provision_router=lambda: None)
    client = app.test_client()
    response = client.get("/api/router/status")

    assert response.status_code in (
        200,
        503,
    )
