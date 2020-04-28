import pytest
import jira
from unittest.mock import MagicMock, patch
import json
import re

jira = jira.Jira(" ", " ", " ")

def okRequestResponse(json_data):
    return {'status_code': 200, 'text': json.dumps(json_data)}

def badRequestResponse(text):
    return {'status_code': 500, 'text': text}


@patch('jira.requests')
@pytest.mark.parametrize('http_code , expected_response', [
    (200, "My connection to Jira is up and running!"),
    (500, "Looks like there's an issue with my connection. I've logged an error")
])
def test_testConnectionCommand(mock_requests, http_code, expected_response):
    mock_requests.request.return_value = MagicMock(status_code=http_code, text='{"text": "some mock test"}')

    response = jira.testConnectionCommand("")

    assert response == {'text': expected_response}

def test_getCommandsRegex():
    expected_response = {
        'test jira': jira.testConnectionCommand,
        'sprint metrics [0-9]+': jira.getSprintMetricsCommand,
        'sprint report [0-9]+': jira.getSprintReportCommand,
        r'sprint report [0-9]+\s*https://www.notion.so/.+': jira.getSprintReportCommand
    }

    assert jira.getCommandsRegex() == expected_response

def test_getCommandDescriptions():
    expected_response = {
        'test jira': 'tests my connection to jira',
        'sprint metrics [sprint-id]': 'get metrics for a given sprint',
        'sprint report [sprint-id]': 'get a quick sprint report for a given sprint',
        'sprint report [sprint-id] [notion-url]': 'get a quick sprint report for a given sprint and update the given notion page'
    }

    assert jira.getCommandDescriptions() == expected_response

# Test Data
sprint_id = '1234'
board_id = '4321'
error_response = "Sorry, I had trouble getting metrics for that sprint. I've logged an error"

valid_sprint_response = okRequestResponse({'originBoardId': 123})

valid_board_response = okRequestResponse({'location': {'projectName' : 'The Best Team', 'projectKey':'TBT'}})

normal_sprint_data = {
    'sprint_report_response' : {
        'sprint': {
            'startDate': '2020-01-01T01:00:00.000Z',
            'endDate': '2020-01-15T01:00:00.000Z',
            'name': 'Sprint 1',
            'goal': 'Goal 1\nGoal 2\nGoal 3'
        },
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
            {
                'key': 'NORMAL-5',
                'typeName': 'Optimization',
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
            "committed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-5'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4', 'NORMAL-5'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 3,
            "completed": 3,
            "not_completed": 0,
            "planned_completed": 3,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 9,
            "completed": 9,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 3,
            "planned_completed": 9,
            "removed": 0,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 100,
            "predictability_of_commitments": 100
        }
    }
}
incomplete_work_sprint_data = {
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
            'issuesNotCompletedInCurrentSprint': [
                {
                    'key': 'INCOMPLETE-1',
                    'typeName': 'Story',
                    'estimateStatistic': {
                        'statFieldValue': {
                                'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'INCOMPLETE-2',
                    'typeName': 'Bug',
                    'estimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'INCOMPLETE-3',
                    'typeName': 'Epic',
                    'estimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'INCOMPLETE-4',
                    'typeName': 'Task',
                    'estimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'INCOMPLETE-5',
                    'typeName': 'Story',
                }
            ],
            'puntedIssues': {}
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2', 'INCOMPLETE-1', 'INCOMPLETE-2', 'INCOMPLETE-5'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4'],
        "incomplete": ['INCOMPLETE-1', 'INCOMPLETE-2', 'INCOMPLETE-3', 'INCOMPLETE-4', 'INCOMPLETE-5'],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 5,
            "completed": 2,
            "not_completed": 3,
            "planned_completed": 2,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 8,
            "completed": 6,
            "feature_completed": 3,
            "not_completed": 2,
            "optimization_completed": 0,
            "planned_completed": 6,
            "removed": 0,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 75,
            "predictability_of_commitments": 75
        }
    }
}
punted_sprint_data = {
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
            'puntedIssues': [
                {
                    'key': 'PUNTED-1',
                    'typeName': 'Story',
                    'estimateStatistic': {
                        'statFieldValue': {
                                'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'PUNTED-2',
                    'typeName': 'Bug',
                    'estimateStatistic': {
                        'statFieldValue': {
                                'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'PUNTED-3',
                    'typeName': 'Epic',
                    'estimateStatistic': {
                        'statFieldValue': {
                                'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'PUNTED-4',
                    'typeName': 'Task',
                    'estimateStatistic': {
                        'statFieldValue': {
                                'value': 1
                        }
                    },
                    'currentEstimateStatistic': {
                        'statFieldValue': {
                            'value': 1
                        }
                    }
                },
                {
                    'key': 'PUNTED-5',
                    'typeName': 'Story'
                }
            ],
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2', 'PUNTED-1', 'PUNTED-2', 'PUNTED-5'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4'],
        "incomplete": [],
        "removed": ['PUNTED-1', 'PUNTED-2', 'PUNTED-3', 'PUNTED-4', 'PUNTED-5']
        },
        "items": {
            "bugs_completed": 1,
            "committed": 5,
            "completed": 2,
            "not_completed": 0,
            "planned_completed": 2,
            "removed": 3,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 8,
            "completed": 6,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 6,
            "removed": 2,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 75,
            "predictability_of_commitments": 75
        }
    }
}
added_sprint_data = {
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
            {
                'key': 'ADDED-1',
                'typeName': 'Story',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 1
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 3
                    }
                }
            },
            {
                'key': 'ADDED-2',
                'typeName': 'Bug',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 1
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 1
                    }
                }
            },
            {
                'key': 'ADDED-3',
                'typeName': 'Epic',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 1
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 1
                    }
                }
            },
            {
                'key': 'ADDED-4',
                'typeName': 'Task',
                'estimateStatistic': {
                    'statFieldValue': {
                            'value': 1
                    }
                },
                'currentEstimateStatistic': {
                    'statFieldValue': {
                        'value': 1
                    }
                }
            },
        ],
            'issueKeysAddedDuringSprint': {'ADDED-1':'', 'ADDED-2':'', 'ADDED-3':'', 'ADDED-4':''},
            'issuesNotCompletedInCurrentSprint': {},
            'puntedIssues': {}
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4', 'ADDED-1', 'ADDED-2', 'ADDED-3', 'ADDED-4'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 2,
            "committed": 2,
            "completed": 4,
            "not_completed": 0,
            "planned_completed": 2,
            "removed": 0,
            "stories_completed": 2,
            "unplanned_bugs_completed": 1,
            "unplanned_completed": 2,
            "unplanned_stories_completed": 1
        },
        "points": {
            "committed": 6,
            "completed": 10,
            "feature_completed": 6,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 6,
            "removed": 0,
            "unplanned_completed": 4
        },
        "meta": {
            "predictability": 166,
            "predictability_of_commitments": 100
        }
    }
}
changed_estimate_sprint_data = {
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
                        'value': 6
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
            "completed": 9,
            "feature_completed": 6,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 9, # This is a point of contention among the SM's but is a crazy edge case
            "removed": 0,
            "unplanned_completed": 3
        },
        "meta": {
            "predictability": 150,
            "predictability_of_commitments": 150
        }
    }
}
no_estimate_sprint_data = {
    'sprint_report_response' : {
        'sprint': {
            'startDate': '2020-01-01T01:00:00.000Z',
            'endDate': '2020-01-15T01:00:00.000Z',
            'name': 'Sprint 1',
            'goal': 'Goal 1\nGoal 2\nGoal 3'
        },
        'contents' : {
            'completedIssues': [
            {
                'key': 'NORMAL-1',
                'typeName': 'Story',
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
            "committed": 3,
            "completed": 3,
            "feature_completed": 0,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 3,
            "removed": 0,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 100,
            "predictability_of_commitments": 100
        }
    }
}
no_committment_sprint_data = {
    'sprint_report_response' : {
        'sprint': {
            'startDate': '2020-01-01T01:00:00.000Z',
            'endDate': '2020-01-15T01:00:00.000Z',
            'name': 'Sprint 1',
            'goal': 'Goal 1\nGoal 2\nGoal 3'
        },
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
            {
                'key': 'NORMAL-5',
                'typeName': 'Optimization',
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
            'issueKeysAddedDuringSprint': {'NORMAL-1':'', 'NORMAL-2':'', 'NORMAL-3':'', 'NORMAL-4':'', 'NORMAL-5':''},
            'issuesNotCompletedInCurrentSprint': {},
            'puntedIssues': {}
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": [],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4', 'NORMAL-5'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 0,
            "completed": 3,
            "not_completed": 0,
            "planned_completed": 0,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 1,
            "unplanned_completed": 3,
            "unplanned_stories_completed": 1
        },
        "points": {
            "committed": 0,
            "completed": 9,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 3,
            "planned_completed": 0,
            "removed": 0,
            "unplanned_completed": 9
        },
        "meta": {
            "predictability": 0,
            "predictability_of_commitments": 0
        }
    }
}
no_goals_or_dates_sprint_data = {
    'sprint_report_response' : {
        'sprint': {
            'name': 'Sprint 1',
        },
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
            {
                'key': 'NORMAL-5',
                'typeName': 'Optimization',
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
            "committed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-5'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4', 'NORMAL-5'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 3,
            "completed": 3,
            "not_completed": 0,
            "planned_completed": 3,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 9,
            "completed": 9,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 3,
            "planned_completed": 9,
            "removed": 0,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 100,
            "predictability_of_commitments": 100
        }
    }
}
no_sprint_number_sprint_data = {
    'sprint_report_response' : {
        'sprint': {
            'name': 'Sprint Blah',
        },
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
            {
                'key': 'NORMAL-5',
                'typeName': 'Optimization',
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
            "committed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-5'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4', 'NORMAL-5'],
        "incomplete": [],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 3,
            "completed": 3,
            "not_completed": 0,
            "planned_completed": 3,
            "removed": 0,
            "stories_completed": 1,
            "unplanned_bugs_completed": 0,
            "unplanned_completed": 0,
            "unplanned_stories_completed": 0
        },
        "points": {
            "committed": 9,
            "completed": 9,
            "feature_completed": 3,
            "not_completed": 0,
            "optimization_completed": 3,
            "planned_completed": 9,
            "removed": 0,
            "unplanned_completed": 0
        },
        "meta": {
            "predictability": 100,
            "predictability_of_commitments": 100
        }
    }
}

@patch('jira.requests')
@pytest.mark.parametrize('message, sprint_get_response, report_get_response, board_get_response,  expected_response', [
    ('sprint metrics 1234', badRequestResponse('No Sprint Found!'), {}, {}, error_response),
    ('sprint metrics abcd', {}, {}, {}, "Sorry, I don't see a valid sprint number there"),
    ('sprint metrics 1234', {}, badRequestResponse('No Board Found!'), {},  error_response),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']), valid_board_response, normal_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(incomplete_work_sprint_data['sprint_report_response']), valid_board_response, incomplete_work_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(punted_sprint_data['sprint_report_response']), valid_board_response, punted_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(added_sprint_data['sprint_report_response']), valid_board_response, added_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(changed_estimate_sprint_data['sprint_report_response']), valid_board_response, changed_estimate_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(no_estimate_sprint_data['sprint_report_response']), valid_board_response, no_estimate_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(no_committment_sprint_data['sprint_report_response']), valid_board_response, no_committment_sprint_data['expected_response']),
])
def test_getSprintMetricsCommand(mock_requests, message, sprint_get_response, report_get_response, board_get_response, expected_response):

    def request_side_effect(verb, url, *args, **kwargs):
        if 'sprint/' in url:
            return MagicMock(**sprint_get_response)
        if 'rapid/charts/sprintreport' in url:
            return MagicMock(**report_get_response)
        if 'board/' in url:
            return MagicMock(**board_get_response)

    mock_requests.request.side_effect = request_side_effect

    response = jira.getSprintMetricsCommand(message)

    if isinstance(expected_response,dict):
        strip_blockqoutes = re.compile('```([^`]*)```', re.MULTILINE)
        result_dict = json.loads(strip_blockqoutes.match(response['text']).group(1))

        assert result_dict == expected_response
    else:
        assert response == {'text': expected_response}


velocity_response = {
    'velocity_get_response': {
        'velocityStatEntries': {
            '0' : {
                'estimated': {
                    'value': 50.0
                },
                'completed': {
                    'value': 50.0
                }
            },
            '2': {
                'estimated': {
                    'value': 5.0
                },
                'completed' : {
                    'value': 5.0
                }
            },
            '3': {
                'estimated': {
                    'value': 10.0
                },
                'completed' : {
                    'value': 10.0
                }
            },
            '4': {
                'estimated': {
                    'value': 20.0
                },
                'completed': {
                    'value': 20.0
                }
            },
            '1': {
                'estimated': {
                    'value': 100.0
                },
                'completed': {
                    'value': 100.0
                }
            }
        }
    },
    'expected_response': 11
}

no_sprints_velocity_response = {
    'velocity_get_response': {
        'velocityStatEntries': {
        }
    },
    'expected_response': 0
}

only_two_velocity_response = {
    'velocity_get_response' : {
        'velocityStatEntries': {
            '1': {
                'estimated': {
                    'value': 5.0
                },
                'completed' : {
                    'value': 5.0
                }
            },
            '2': {
                'estimated': {
                    'value': 10.0
                },
                'completed' : {
                    'value': 10.0
                }
            }
        }
    },
    'expected_response': 7
}

specific_velocity_response = {
    'velocity_get_response': {
        'velocityStatEntries': {
            '0' : {
                'estimated': {
                    'value': 50.0
                },
                'completed': {
                    'value': 50.0
                }
            },
            '2': {
                'estimated': {
                    'value': 5.0
                },
                'completed' : {
                    'value': 5.0
                }
            },
            '3': {
                'estimated': {
                    'value': 10.0
                },
                'completed' : {
                    'value': 10.0
                }
            },
            '4': {
                'estimated': {
                    'value': 20.0
                },
                'completed': {
                    'value': 20.0
                }
            },
            '1': {
                'estimated': {
                    'value': 100.0
                },
                'completed': {
                    'value': 100.0
                }
            }
        }
    },
    'expected_response': 38
}

@patch('jira.requests')
@pytest.mark.parametrize('velocity_get_response, sprint_id, expected_response', [
    (okRequestResponse(velocity_response['velocity_get_response']), None,  velocity_response['expected_response']),
    (okRequestResponse(no_sprints_velocity_response['velocity_get_response']), None, no_sprints_velocity_response['expected_response']),
    (okRequestResponse(only_two_velocity_response['velocity_get_response']), None, only_two_velocity_response['expected_response']),
    (okRequestResponse(specific_velocity_response['velocity_get_response']), "3",  specific_velocity_response['expected_response']),
    (badRequestResponse('No Velocity Report'), None, Exception("Unable to get velocity report for board 1234"))
])
def test_getAverageVelocity(mock_requests, velocity_get_response, sprint_id,  expected_response):
    def request_side_effect(verb, url, *args, **kwargs):
        print(url)
        return MagicMock(**velocity_get_response)

    mock_requests.request.side_effect = request_side_effect

    if isinstance(expected_response, Exception):
        with pytest.raises(Exception, match=str(expected_response)):
            assert jira.getAverageVelocity('1234', sprint_id) == expected_response
    else:
        assert jira.getAverageVelocity('1234', sprint_id) == expected_response

valid_report = {
    'sprint_number': '1',
    'sprint_start': '2020-01-01T01:00:00.000Z',
    'sprint_end': '2020-01-15T01:00:00.000Z',
    'issue_metrics': normal_sprint_data['expected_response'],
    'sprint_goals': ['Goal 1', 'Goal 2', 'Goal 3'],
    'project_name': "The Best Team",
    'project_key': 'TBT',
    'average_velocity': 21
}

report_velocity_response = {
    'velocity_get_response': {
        'velocityStatEntries': {
            '1234' : {
                'estimated': {
                    'value': 50.0
                },
                'completed': {
                    'value': 50.0
                }
            },
            '1233': {
                'estimated': {
                    'value': 5.0
                },
                'completed' : {
                    'value': 5.0
                }
            },
            '1232': {
                'estimated': {
                    'value': 10.0
                },
                'completed' : {
                    'value': 10.0
                }
            }
        }
    }
}

@patch('jira.requests')
@pytest.mark.parametrize('sprint_id, sprint_get_response, report_get_response, board_get_response, velocity_get_response, expected_response', [
    ('5432', badRequestResponse('No Sprint Found!'), {}, {}, {}, Exception("Could not find sprint with id 5432")),
    ('5432', valid_sprint_response, {}, badRequestResponse('No Report Found!'), {}, Exception("Could not find report for sprint 5432 on board 123")),
    ('1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  badRequestResponse('No Board Found!'), okRequestResponse(report_velocity_response['velocity_get_response']), Exception('Could not find boad with id 123')),
    ('1234', valid_sprint_response, okRequestResponse(no_goals_or_dates_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), Exception('Could not find or parse sprint goal')),
    ('1234', valid_sprint_response, okRequestResponse(no_sprint_number_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), Exception('Could not find or parse sprint number')),
    ('1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), valid_report)
])
def test_generateAllSprintReportData(mock_requests, sprint_id, sprint_get_response, report_get_response, board_get_response, velocity_get_response, expected_response):
    def request_side_effect(verb, url, *args, **kwargs):
        if 'sprint/' in url:
            return MagicMock(**sprint_get_response)
        if 'rapid/charts/sprintreport' in url:
            return MagicMock(**report_get_response)
        if 'board/' in url:
            return MagicMock(**board_get_response)
        if 'rapid/charts/velocity' in url:
            return MagicMock(**velocity_get_response)

    mock_requests.request.side_effect = request_side_effect

    if isinstance(expected_response, Exception):
        with pytest.raises(Exception, match=str(expected_response)):
            jira.generateAllSprintReportData(sprint_id)
    else:
        assert jira.generateAllSprintReportData(sprint_id) == expected_response

valid_google_form_url='https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/viewform?entry.1082637073=TBT&entry.1975251686=1&entry.448087930=1&entry.2095001800=3&entry.1399119358=3&entry.128659456=0&entry.954885633=3&entry.1137054034=0&entry.1980453543=1&entry.1252702382=0&entry.485777497=0&entry.370334542=0&entry.1427603868=9&entry.1486076673=9&entry.254612996=3&entry.611444996=0&entry.2092919144=3&entry.493624591=9&entry.976792423=0&entry.1333444050=0&'

@pytest.mark.parametrize('sprint_report_data, expected_response', [
    (valid_report, valid_google_form_url),
    ({}, Exception('Unable to generate Google Form URL, expected keys missing'))
])
def test_generateGoogleFormURL(sprint_report_data, expected_response):

    if isinstance(expected_response, Exception):
        with pytest.raises(Exception, match=str(expected_response)):
            jira.generateGoogleFormURL(sprint_report_data)
    else:
        assert jira.generateGoogleFormURL(sprint_report_data) == expected_response

validNotionReplacementDictionary = {
    '[sprint-number]': '1',
    '[sprint-start]': '01/01/2020',
    '[sprint-end]': '01/15/2020',
    '[sprint-goal]': 'Goal 1\nGoal 2\nGoal 3',
    '[team-name]': "The Best Team",
    '[average-velocity]': '21',
    '[points-committed]': '9',
    '[points-completed]': '9',
    '[items-committed]': '3',
    '[items-completed]': '3',
    '[bugs-completed]': '1',
    '[predictability]': '100%',
    '[predictability-commitments]': '100%',
    '[average-velocity]': '21',
    '[original-committed-link]': "[3 Committed Issues](https://thetower.atlassian.net/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-5))",
    '[completed-issues-link]': "[3 Completed Issues](https://thetower.atlassian.net/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-3%2CNORMAL-4%2CNORMAL-5))",
    '[items-not-completed-link]': "[0 Incomplete Issues](https://thetower.atlassian.net/issues/?jql=issueKey%20in%20())",
    '[items-removed-link]': "[0 Removed Issues](https://thetower.atlassian.net/issues/?jql=issueKey%20in%20())"
}

@pytest.mark.parametrize('sprint_report_data, expected_response', [
    ({}, Exception("Unable to generate a Notion Replacement Dictionary, keys not found")),
    (valid_report, validNotionReplacementDictionary)
])
def test_generateNotionReplacementDictionary(sprint_report_data, expected_response):
    if isinstance(expected_response, Exception):
        with pytest.raises(Exception, match=str(expected_response)):
            jira.generateNotionReplacementDictionary(sprint_report_data)
    else:

        actual_response = jira.generateNotionReplacementDictionary(sprint_report_data)

        for key in sorted(expected_response):
            assert expected_response[key] == actual_response[key]

@pytest.mark.parametrize('issue_numbers, expected_response', [
    (normal_sprint_data['expected_response']['issue_keys']['completed'], "https://thetower.atlassian.net/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-3%2CNORMAL-4%2CNORMAL-5)"),
    ([], "https://thetower.atlassian.net/issues/?jql=issueKey%20in%20()")
])
def test_generateJiraIssueLink(issue_numbers, expected_response):
    assert jira.generateJiraIssueLink(issue_numbers) == expected_response



valid_blocks = {'blocks': [{'alt_text': 'Order Up!',
                          'image_url': 'https://media.giphy.com/media/l1JojmmBMELYFKJc4/giphy.gif',
                          'title': {'text': 'Order Up!', 'type': 'plain_text'},
                          'type': 'image'},
                         {'type': 'divider'},
                         {'text': {'text': '*Project Name*: The Best Team\n'
                                           '*Sprint 1*\n'
                                           'Goal 1\n'
                                           'Goal 2\n'
                                           'Goal 3',
                                   'type': 'mrkdwn'},
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '*Metrics:*', 'type': 'mrkdwn'},
                          'type': 'section'},
                         {'text': {'text': '*items*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'stories_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'unplanned_stories_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'bugs_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'},
                                     {'text': 'unplanned_bugs_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*points*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'feature_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'optimization_completed',
                                      'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*meta*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'predictability', 'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'},
                                     {'text': 'predictability_of_commitments',
                                      'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '<https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/viewform?entry.1082637073=TBT&entry.1975251686=1&entry.1427603868=9&entry.1486076673=9&entry.493624591=9&entry.1333444050=0&entry.254612996=3&entry.2092919144=3&entry.611444996=0&entry.976792423=0&entry.2095001800=3&entry.1399119358=3&entry.954885633=3&entry.485777497=0&entry.1980453543=1&entry.370334542=0&entry.448087930=1&entry.1252702382=0&entry.128659456=0&entry.1137054034=0&|Google '
                                           'Form URL>',
                                   'type': 'mrkdwn'},
                          'type': 'section'}]}

valid_notion_blocks = {'blocks': [{'alt_text': 'Order Up!',
                          'image_url': 'https://media.giphy.com/media/l1JojmmBMELYFKJc4/giphy.gif',
                          'title': {'text': 'Order Up!', 'type': 'plain_text'},
                          'type': 'image'},
                         {'type': 'divider'},
                         {'text': {'text': '*Project Name*: The Best Team\n'
                                           '*Sprint 1*\n'
                                           'Goal 1\n'
                                           'Goal 2\n'
                                           'Goal 3',
                                   'type': 'mrkdwn'},
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '*Metrics:*', 'type': 'mrkdwn'},
                          'type': 'section'},
                         {'text': {'text': '*items*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'stories_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'unplanned_stories_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'bugs_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'},
                                     {'text': 'unplanned_bugs_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*points*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'feature_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'optimization_completed',
                                      'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*meta*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'predictability', 'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'},
                                     {'text': 'predictability_of_commitments',
                                      'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '<https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/viewform?entry.1082637073=TBT&entry.1975251686=1&entry.1427603868=9&entry.1486076673=9&entry.493624591=9&entry.1333444050=0&entry.254612996=3&entry.2092919144=3&entry.611444996=0&entry.976792423=0&entry.2095001800=3&entry.1399119358=3&entry.954885633=3&entry.485777497=0&entry.1980453543=1&entry.370334542=0&entry.448087930=1&entry.1252702382=0&entry.128659456=0&entry.1137054034=0&|Google '
                                           'Form URL>',
                                   'type': 'mrkdwn'},
                          'type': 'section'},
                          {'type': 'divider'},
                          {
                              "type": "section",
                              "text": {
                                  "type": "mrkdwn",
                                  "text": "<https://www.notion.so/mediaos/some-test-document|Notion Page> updated!"
                              }
                              }]
                              }

notion_error_blocks = {'blocks': [{'alt_text': 'Order Up!',
                          'image_url': 'https://media.giphy.com/media/l1JojmmBMELYFKJc4/giphy.gif',
                          'title': {'text': 'Order Up!', 'type': 'plain_text'},
                          'type': 'image'},
                         {'type': 'divider'},
                         {'text': {'text': '*Project Name*: The Best Team\n'
                                           '*Sprint 1*\n'
                                           'Goal 1\n'
                                           'Goal 2\n'
                                           'Goal 3',
                                   'type': 'mrkdwn'},
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '*Metrics:*', 'type': 'mrkdwn'},
                          'type': 'section'},
                         {'text': {'text': '*items*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'stories_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'unplanned_stories_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'bugs_completed', 'type': 'plain_text'},
                                     {'text': '1', 'type': 'plain_text'},
                                     {'text': 'unplanned_bugs_completed',
                                      'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*points*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'committed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'planned_completed', 'type': 'plain_text'},
                                     {'text': '9', 'type': 'plain_text'},
                                     {'text': 'unplanned_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'feature_completed', 'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'fields': [{'text': 'optimization_completed',
                                      'type': 'plain_text'},
                                     {'text': '3', 'type': 'plain_text'},
                                     {'text': 'not_completed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'},
                                     {'text': 'removed', 'type': 'plain_text'},
                                     {'text': '0', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'text': {'text': '*meta*', 'type': 'mrkdwn'}, 'type': 'section'},
                         {'fields': [{'text': 'predictability', 'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'},
                                     {'text': 'predictability_of_commitments',
                                      'type': 'plain_text'},
                                     {'text': '100', 'type': 'plain_text'}],
                          'type': 'section'},
                         {'type': 'divider'},
                         {'text': {'text': '<https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/viewform?entry.1082637073=TBT&entry.1975251686=1&entry.1427603868=9&entry.1486076673=9&entry.493624591=9&entry.1333444050=0&entry.254612996=3&entry.2092919144=3&entry.611444996=0&entry.976792423=0&entry.2095001800=3&entry.1399119358=3&entry.954885633=3&entry.485777497=0&entry.1980453543=1&entry.370334542=0&entry.448087930=1&entry.1252702382=0&entry.128659456=0&entry.1137054034=0&|Google '
                                           'Form URL>',
                                   'type': 'mrkdwn'},
                          'type': 'section'},
                          {'type': 'divider'},
                          {
                              "type": "section",
                              "text": {
                                  "type": "mrkdwn",
                                  "text": "There was an error updating the <https://www.notion.so/mediaos/some-test-document|Notion Page>."
                              }
                              }]
                              }

valid_notion_case = {
    'dictionary': validNotionReplacementDictionary,
    'exception': False
}

error_notion_case = {
    'dictionary': validNotionReplacementDictionary,
    'exception': True
}

@patch('jira.NotionPage')
@patch('jira.requests')
@pytest.mark.parametrize('message_text, sprint_get_response, report_get_response, board_get_response, velocity_get_response, notion_case, expected_response', [
    ('sprint report 5432', badRequestResponse('No Sprint Found!'), {}, {}, {}, False, {'text': "Sorry, I had trouble generating a report for that sprint. I've logged an error"}),
    ('sprint report 1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), False, valid_blocks),
    ('sprint report 1234 https://www.notion.so/mediaos/some-test-document', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), valid_notion_case, valid_notion_blocks),
    ('sprint report 1234 https://www.notion.so/mediaos/some-test-document', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), error_notion_case, notion_error_blocks)
])
def test_getSprintReportCommand(mock_requests, mock_notion_page, message_text, sprint_get_response, report_get_response, board_get_response, velocity_get_response, notion_case, expected_response):
    def request_side_effect(verb, url, *args, **kwargs):
        if 'sprint/' in url:
            return MagicMock(**sprint_get_response)
        if 'rapid/charts/sprintreport' in url:
            return MagicMock(**report_get_response)
        if 'board/' in url:
            return MagicMock(**board_get_response)
        if 'rapid/charts/velocity' in url:
            return MagicMock(**velocity_get_response)

    mock_requests.request.side_effect = request_side_effect

    if notion_case:
        mock_notion_page.return_value = mock_notion_page

        if notion_case['exception']:
            mock_notion_page.searchAndReplace.side_effect = lambda x: exec(f"raise(Exception())")


    if isinstance(expected_response, Exception):
        with pytest.raises(Exception, match=str(expected_response)):
            jira.getSprintReportCommand(message_text)
    else:
        assert jira.getSprintReportCommand(message_text) == expected_response

    if notion_case:
        mock_notion_page.searchAndReplace.assert_called_once_with(notion_case['dictionary'])
