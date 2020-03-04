import pytest
import jr

@pytest.fixture
def client():
    with jr.app.test_client() as client:
        yield client

def test_healthcheck(client):
    rv = client.get('/health')

    assert 200 is rv.status_code
