import pytest
import jira
from unittest.mock import MagicMock, patch

jira = jira.Jira(" ", " ", " ")

@patch('jira.requests')
@pytest.mark.parametrize('http_code , expected_response', [
    (200, "My connection to Jira is up and running!"),
    (500, "Looks like there's an issue with my connection. I've logged an error")
])
def test_testConnectionCommand(mock_requests, http_code, expected_response):
    mock_requests.request.return_value = MagicMock(status_code=http_code, text='{"text": "some mock test"}')

    response = jira.testConnectionCommand("")

    assert response == expected_response

def test_getCommandsRegex():
    expected_response = {
        'test jira': jira.testConnectionCommand,
        'sprint metrics [0-9]+': jira.getSprintMetricsCommand
    }

    assert jira.getCommandsRegex() == expected_response

def test_getCommandDescriptions():
    expected_response = {
        'test jira': 'tests my connection to jira',
        'sprint metrics [sprint-id]': 'get metrics for a given sprint'
    }

    assert jira.getCommandDescriptions() == expected_response
