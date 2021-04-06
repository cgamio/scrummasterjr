import json

def okRequestResponse(json_data):
    return {'status_code': 200, 'text': json.dumps(json_data)}

def badRequestResponse(text):
    return {'status_code': 500, 'text': text}

# Test Data
sprint_id = '1234'
board_id = '4321'
error_response = "Sorry, I had trouble getting metrics for that sprint. I've logged an error"
jira_test_instance = "example.atlassian.net"

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
            "committed": 3,
            "completed": 3,
            "planned_completed": 3,
            "unplanned_completed": 0,
            "stories_completed": 1,
            "unplanned_stories_completed": 0,
            "bugs_completed": 1,
            "unplanned_bugs_completed": 0,
            "not_completed": 0,
            "removed": 0
        },
        "points": {
            "committed": 9,
            "completed": 9,
            "planned_completed": 9,
            "unplanned_completed": 0,
            "feature_completed": 3,
            "optimization_completed": 3,
            "not_completed": 0,
            "removed": 0

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

valid_google_form_url='https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/formResponse?entry.1082637073=TBT&entry.1975251686=1&entry.2095001800=3&entry.1399119358=3&entry.954885633=3&entry.485777497=0&entry.1980453543=1&entry.370334542=0&entry.448087930=1&entry.1252702382=0&entry.128659456=0&entry.1137054034=0&entry.1427603868=9&entry.1486076673=9&entry.493624591=9&entry.1333444050=0&entry.254612996=3&entry.2092919144=3&entry.611444996=0&entry.976792423=0&submit=Submit'


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
    '[original-committed-link]': f"[3 Committed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-5))",
    '[completed-issues-link]': f"[3 Completed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-3%2CNORMAL-4%2CNORMAL-5))",
    '[items-not-completed-link]': f"[0 Incomplete Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20())",
    '[items-removed-link]': f"[0 Removed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20())"
}

validNextSprintNotionReplacementDictionary = {
    '[next-sprint-number]': '1',
    '[next-sprint-start]': '01/01/2020',
    '[next-sprint-end]': '01/15/2020',
    '[next-sprint-goal]': 'Goal 1\nGoal 2\nGoal 3',
    '[next-points-committed]': '9',
    '[next-items-committed]': '3',
    '[next-original-committed-link]': f"[3 Committed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-5))"
}

validTwoSprintNotionReplacementDictionary = {
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
    '[original-committed-link]': f"[3 Committed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-5))",
    '[completed-issues-link]': f"[3 Completed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-3%2CNORMAL-4%2CNORMAL-5))",
    '[items-not-completed-link]': f"[0 Incomplete Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20())",
    '[items-removed-link]': f"[0 Removed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20())",
    '[next-sprint-number]': '1',
    '[next-sprint-start]': '01/01/2020',
    '[next-sprint-end]': '01/15/2020',
    '[next-sprint-goal]': 'Goal 1\nGoal 2\nGoal 3',
    '[next-points-committed]': '9',
    '[next-items-committed]': '3',
    '[next-original-committed-link]': f"[3 Committed Issues](https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-5))"
}

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
                         {'text': {'text': f'<{valid_google_form_url}|Google '
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
                         {'text': {'text': f'<{valid_google_form_url}|Google '
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

notion_error_blocks = ({'blocks': [{'alt_text': 'Order Up!',
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
                                  "text": "There was an error updating the <https://www.notion.so/mediaos/some-test-document|Notion Page>. I've notified my overlords and I'm sure they're looking into it"
                              }
                              }]
                              }, 'A user trying to update a Notion page got the following error. You might want to check / update the Notion token\n `An Error!`')

valid_notion_case = {
    'dictionary': validTwoSprintNotionReplacementDictionary,
    'exception': False
}

error_notion_case = {
    'dictionary': validTwoSprintNotionReplacementDictionary,
    'exception': True
}
