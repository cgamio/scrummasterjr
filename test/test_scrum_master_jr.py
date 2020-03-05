import pytest
import scrum_master_jr
from unittest.mock import MagicMock

@pytest.fixture
def client():
    with scrum_master_jr.app.test_client() as client:
        yield client

def test_healthcheck(client):
    rv = client.get('/health')

    assert 200 is rv.status_code

def test_help_no_set():
    # Test getting help with no command sets
    default_response = "These are the things I know how to respond to:\nhello - random greeting"

    scrum_master_jr.commandsets = []

    response = scrum_master_jr.get_help("help")
    assert response == default_response

def test_help_mock_set():
    # Test getting help with a Mock command set
    set = MagicMock()
    set.getCommandDescriptions.return_value = {"some command": "does a test thing"}

    scrum_master_jr.commandsets = [set]

    expected_response = "These are the things I know how to respond to:\nhello - random greeting\nsome command - does a test thing"
    response = scrum_master_jr.get_help("help")

    set.getCommandDescriptions.assert_called()
    assert response == expected_response
