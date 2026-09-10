from router_controller.router_comms.status_service import RouterStatusService

class FakeRouter:
    def status(self):
        return "router-status"

def test_status_service_returns_router_status():
    service = RouterStatusService(FakeRouter())

    assert service.get_status()=="router-status"
