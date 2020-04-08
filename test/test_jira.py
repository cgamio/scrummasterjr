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

    assert response == expected_response

def test_getCommandsRegex():
    expected_response = {
        'test jira': jira.testConnectionCommand,
        'sprint metrics [0-9]+': jira.getSprintMetricsCommand,
        'sprint report [0-9]+': jira.getSprintReportCommand
    }

    assert jira.getCommandsRegex() == expected_response

def test_getCommandDescriptions():
    expected_response = {
        'test jira': 'tests my connection to jira',
        'sprint metrics [sprint-id]': 'get metrics for a given sprint',
        'sprint report [sprint-id]': 'get a quick sprint report for a given sprint'
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
            'startDate': '01/Jan/20 1:00 AM',
            'endDate': '15/Jan/20 1:00 AM',
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
            ],
            'puntedIssues': {}
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2', 'INCOMPLETE-1', 'INCOMPLETE-2'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4'],
        "incomplete": ['INCOMPLETE-1', 'INCOMPLETE-2', 'INCOMPLETE-3', 'INCOMPLETE-4'],
        "removed": []
        },
        "items": {
            "bugs_completed": 1,
            "committed": 4,
            "completed": 2,
            "not_completed": 2,
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
            ],
        }
    },
    'expected_response': {
        "issue_keys": {
            "committed": ['NORMAL-1', 'NORMAL-2', 'PUNTED-1', 'PUNTED-2'],
            "completed": ['NORMAL-1', 'NORMAL-2', 'NORMAL-3', 'NORMAL-4'],
        "incomplete": [],
        "removed": ['PUNTED-1', 'PUNTED-2', 'PUNTED-3', 'PUNTED-4']
        },
        "items": {
            "bugs_completed": 1,
            "committed": 4,
            "completed": 2,
            "not_completed": 0,
            "planned_completed": 2,
            "removed": 2,
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
                        'value': 1
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
            "completed": 8,
            "feature_completed": 4,
            "not_completed": 0,
            "optimization_completed": 0,
            "planned_completed": 6,
            "removed": 0,
            "unplanned_completed": 2
        },
        "meta": {
            "predictability": 133,
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


@patch('jira.requests')
@pytest.mark.parametrize('message, sprint_get_response, report_get_response, board_get_response,  expected_response', [
    ('sprint metrics 1234', badRequestResponse('No Sprint Found!'), {}, {}, error_response),
    ('sprint metrics 1234', {}, badRequestResponse('No Board Found!'), {},  error_response),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']), valid_board_response, normal_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(incomplete_work_sprint_data['sprint_report_response']), valid_board_response, incomplete_work_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(punted_sprint_data['sprint_report_response']), valid_board_response, punted_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(added_sprint_data['sprint_report_response']), valid_board_response, added_sprint_data['expected_response']),
    ('sprint metrics 1234', valid_sprint_response, okRequestResponse(changed_estimate_sprint_data['sprint_report_response']), valid_board_response, changed_estimate_sprint_data['expected_response']),
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
        result_dict = json.loads(strip_blockqoutes.match(response).group(1))

        assert result_dict == expected_response
    else:
        assert response == expected_response


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
])
def test_getAverageVelocity(mock_requests, velocity_get_response, sprint_id,  expected_response):
    def request_side_effect(verb, url, *args, **kwargs):
        print(url)
        return MagicMock(**velocity_get_response)

    mock_requests.request.side_effect = request_side_effect

    if sprint_id == None:
        assert jira.getAverageVelocity('1234') == expected_response
    else:
        assert jira.getAverageVelocity('1234', sprint_id) == expected_response

valid_report = {
    'sprint_number': '1',
    'sprint_start': '01/Jan/20 1:00 AM',
    'sprint_end': '15/Jan/20 1:00 AM',
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
        with pytest.raises(Exception):
            jira.generateAllSprintReportData(sprint_id)
    else:
        assert jira.generateAllSprintReportData(sprint_id) == expected_response
