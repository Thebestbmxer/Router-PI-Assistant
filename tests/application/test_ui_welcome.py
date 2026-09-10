def test_welcome_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Router Pi Controller" in response.data

#def test_discover_endpoint_returns_not_found(client):


#def test_provision_endpoint_returns_success(client):