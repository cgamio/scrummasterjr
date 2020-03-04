import pytest
import jr

@pytest.fixture
def client():
    with jr.app.test_client() as client:
        yield client

def test_healthcheck(client):
    rv = client.get('/health')

    assert 200 is rv.status_code

def test_help(client):
    default_response = "These are the things I know how to respond to:\nhello - random greeting"

    jr.commandsets = []
    response = jr.get_help("help")
    assert response == default_response

    class TestSet:
        def getCommandDescriptions(self):
            return {"some command": "does a test thing"}

    set = TestSet()
    jr.commandsets = [set]
    expected_response = f"{default_response}\nsome command - does a test thing"
    response = jr.get_help("help")
    assert response == expected_response
