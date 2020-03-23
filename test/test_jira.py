import pytest
import jira
from unittest.mock import MagicMock, patch
import json
import re

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

# Test Data
valid_response = json.dumps({
    "issue_keys": {
    "committed": [
        "MADD-244",
        "MADD-252",
        "MADD-279",
        "MADD-282",
        "MADD-284",
        "MADD-242",
        "MADD-278"
    ],
    "completed": [
    "MADD-244",
    "MADD-252",
    "MADD-253",
    "MADD-279",
    "MADD-282",
    "MADD-284",
    "MADD-286",
    "MADD-287",
    "MADD-290",
    "MADD-291",
        "MADD-294"
    ],
    "incomplete": [
        "MADD-242",
        "MADD-278"
    ],
    "removed": []
    },
    "items": {
        "bugs_completed": 1,
        "committed": 7,
        "completed": 7,
        "not_completed": 2,
        "planned_completed": 5,
        "removed": 0,
        "stories_completed": 6,
        "unplanned_bugs_completed": 1,
        "unplanned_completed": 2,
        "unplanned_stories_completed": 1
    },
    "points": {
        "committed": 23,
        "completed": 16,
        "feature_completed": 16,
        "not_completed": 8,
        "optimization_completed": 0,
        "planned_completed": 15,
        "removed": 0,
        "unplanned_completed": 1
    }
}, sort_keys=True, indent=4, separators=(",", ": "))
valid_response = f"```{valid_response}```"

sprint_id = '1234'
board_id = '4321'
error_response = "Sorry, I had trouble getting metrics for that sprint. I've logged an error"

valid_sprint_response = {'status_code': 200, 'text': json.dumps({ 'originBoardId': 123})}

normal_sprint_data = {
    'sprint_report_response' : {
        'contents' : {
            'completedIssues': [
            {
                'key': 'NORMAL-1',
                'typeName': 'Story',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 3
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 3
                    }
                }
            },
            {
                'key': 'NORMAL-2',
                'typeName': 'Bug',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 3
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 3
                    }
                }
            },
            {
                'key': 'NORMAL-3',
                'typeName': 'Epic',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 3
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 3
                    }
                }
            },
            {
                'key': 'NORMAL-4',
                'typeName': 'Task',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 3
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 3
                    }
                }
            },
        ],
            'issueKeysAddedDuringSprint': {},
            'issuesNotCompletedInCurrentSprint': {},
            'puntedIssues': {}
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 2,
            "completed": 2,
            "not_completed": 0,
            "planned_completed": 2,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 6,
            "completed": 6,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 6,
            "removed": 0,
            "unplanned_completed": 0
        }
    }
}


@patch('jira.requests')
@pytest.mark.parametrize('message, sprint_get_response, report_get_response,  expected_response', [
    ('sprint metrics 1234', {'status_code': 500, 'text': 'No Sprint Found!'}, {}, error_response),
    ('sprint metrics 1234', {}, {'status_code': 500, 'text': 'No Board Found!'}, error_response),
    ('sprint metrics 1234', valid_sprint_response, valid_report_response, valid_response),
    ('sprint metrics 1234', valid_sprint_response, {'status_code': 200, 'text': json.dumps(normal_sprint_data['sprint_report_response'])}, normal_sprint_data['expected_response']),
])
def test_getSprintMetricsCommand(mock_requests, message, sprint_get_response, report_get_response, expected_response):

    def request_side_effect(verb, url, *args, **kwargs):
        if 'sprint/' in url:
            return MagicMock(**sprint_get_response)
        if 'rapid/charts/sprintreport' in url:
            return MagicMock(**report_get_response)

    mock_requests.request.side_effect = request_side_effect

    assert jira.getSprintMetricsCommand(message) == expected_response
