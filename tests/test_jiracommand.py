import pytest
from scrummasterjr.jiracommand import JiraCommand
from scrummasterjr.error import ScrumMasterJrError
from unittest.mock import MagicMock, patch, call
from fixtures import *

@pytest.fixture
def command():
    command = JiraCommand(None)
    command.jira = MagicMock()

    return command

@pytest.fixture
def selected_board_id(autouse = True):
    return 123

@pytest.fixture
def board_select_body_block(autouse = True):
    return {
        "type": "placeholder"
    }

@pytest.fixture
def body_with_selected_board(autouse = True):
    return {
        "actions": [
            {
                "selected_option": {
                    "value": selected_board_id
                }
            }
        ],
        "view": {
            "blocks": [board_select_body_block],
            "hash": "abc123",
            "id": "qwerty",
            "type": "modal",
            "title": {
        		"type": "plain_text",
        		"text": "Some Test Modal"
        	}
        }
    }

@pytest.fixture
def selected_complete_sprint_id(autouse = True):
    return "nfjdn28"

@pytest.fixture
def selected_upcoming_sprint_id(autouse = True):
    return "asdf9dmdf"

@pytest.fixture
def body_with_all_inputs(selected_board_id, selected_complete_sprint_id, selected_upcoming_sprint_id):
    return {
        "view": {
            "state": {
                "values": {
                    "board_section": {
                        "board_select_action": {
                            "selected_option": {
                                "value": selected_board_id
                            }
                        }
                    },
                    "completed_sprint_section": {
                        "blah": {
                            "selected_option": {
                                "value": selected_complete_sprint_id
                            }
                        }
                    },
                    "upcoming_sprint_section": {
                        "bleh": {
                            "selected_option": {
                                "value": selected_upcoming_sprint_id
                            }
                        }
                    },
                    'notion_url_block': {
                        'notion_url_input_action': {
                            'value': None
                        }
                    }
                }
            },
        "type": "modal",
        "title": {
    		"type": "plain_text",
    		"text": "Some Test Modal"
    	}
        }
    }

@pytest.mark.parametrize('jira_response, expected_response', [
    (200, "My connection to Jira is up and running!"),
    (None, "Looks like there's an issue with my connection. I've logged an error")
])
def test_testConnectionCommand(command, jira_response, expected_response):
    command.jira.testConnection.return_value = jira_response

    response = command.testConnection(None)

    assert response == expected_response

bad_sprint_error = ScrumMasterJrError('Something Bad', 'Something Specifically Bad')
google_form_url_error = ScrumMasterJrError('Something Bad', 'Something Specifically Bad')
bad_notion_error = ScrumMasterJrError(notion_error_blocks)

@pytest.mark.parametrize('slack_event, all_sprint_data_input, all_sprint_data_response, notion_url, update_notion_page_response, generate_google_form_url_response, expected_response', [
    ({'text': 'sprint report 5432'}, ['5432'], [bad_sprint_error], None, None, None, bad_sprint_error),
    ({'text': 'sprint report 1234'}, ['1234'], [valid_report], None, None, valid_google_form_url, valid_blocks),
    ({'text': 'sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document'}, ['1234', '5678'], [valid_report, valid_report], "https://www.notion.so/mediaos/some-test-document", valid_notion_case, valid_google_form_url, valid_notion_blocks),
    ({'text': 'sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document'}, ['1234', '5678'], [valid_report, valid_report], "https://www.notion.so/mediaos/some-test-document", bad_notion_error, valid_google_form_url, bad_notion_error),
])
def test_getSprintReport(command, slack_event, all_sprint_data_input, all_sprint_data_response, notion_url, update_notion_page_response, generate_google_form_url_response, expected_response):


    if isinstance(update_notion_page_response, Exception):
        command.jira.updateNotionPage.return_value = update_notion_page_response
    else:
        command.jira.updateNotionPage.return_value = None

    command.jira.generateAllSprintReportData.side_effect = all_sprint_data_response

    if generate_google_form_url_response:
        command.jira.generateGoogleFormURL.return_value = generate_google_form_url_response

        if isinstance(generate_google_form_url_response, Exception):
            command.jira.generateGoogleFormURL.side_effect = lambda x: exec(f"raise(ScrumMasterJrError('An Error!'))")

    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            command.getSprintReport(slack_event)
    else:
        assert command.getSprintReport(slack_event) == expected_response

    if all_sprint_data_response:
        command.jira.generateAllSprintReportData.assert_has_calls(map(call, all_sprint_data_input))

    if update_notion_page_response and not isinstance(update_notion_page_response, Exception):
        command.jira.updateNotionPage.assert_called_once_with(notion_url, *all_sprint_data_response)

@pytest.mark.parametrize('jira_response, response', [
    (None, {"text": "Please provide a valid Jira Project Key with this command", "response_type": "ephemeral"}),
    ({"values": []}, {"text": "I'm only able to generate sprint reports for projects that use Scrum boards. Please reach out in <#C6GJGERFC> if you need help getting one set up.", "response_type": "ephemeral"}),
    ({"values": [{"type":"not-scrum"}]}, {"text": "I'm only able to generate sprint reports for projects that use Scrum boards. Please reach out in <#C6GJGERFC> if you need help getting one set up.", "response_type": "ephemeral"})
])
def test_showSprintReportModal_errors(command, jira_response, response):
    command.jira.getBoardsInProject.return_value = jira_response

    mock_respond = MagicMock()
    mock_ack = MagicMock()

    command.showSprintReportModal(mock_ack, None, None, {"text": " test "}, mock_respond)

    mock_ack.assert_called()
    command.jira.getBoardsInProject.assert_called_once_with("test")
    mock_respond.assert_called_once_with(response)

def test_showSprintReportModal_valid(command):
    valid_boards = {
        "values": [
            {
                "type": "scrum",
                "name": "First Test Board",
                "id": 1
            },
            {
                "type": "scrum",
                "name": "Second Test Board",
                "id": 2
            }
        ]
    }

    valid_body = {
        "trigger_id": "abc123"
    }

    def check_client_views_open(trigger_id, view):
        assert trigger_id == valid_body.trigger_id

        assert view["blocks"][0]["element"]["options"] == [
            {
                "text": {
                    "type": "plain_text",
                    "text": "First Test Board"
                },
                "value": 1
            },
            {
                "text": {
                    "type": "plain_text",
                    "text": "Second Test Board"
                },
                "value": 2
            }
        ]


    command.jira.getBoardsInProject.return_value = valid_boards
    mock_ack = MagicMock()
    mock_client = MagicMock()

    command.showSprintReportModal(mock_ack, valid_body, mock_client, {"text": " test "}, None)

    command.jira.getBoardsInProject.assert_called_once_with("test")
@pytest.mark.parametrize('sprints_in_boards_values', [
    ([]),
    ([
        {
            "name": "Sprint 1",
            "state": "closed",
            "id": 1
        },
        {
            "name": "Sprint 2",
            "state": "active",
            "id": 2
        }
    ])
])
def test_showSprints_no_sprints(command, body_with_selected_board, sprints_in_boards_values):
    mock_ack = MagicMock()
    mock_client = MagicMock()
    command.jira.getSprintsInBoard.return_value = sprints_in_boards_values

    command.showSprints(mock_ack, body_with_selected_board, mock_client)

    mock_ack.assert_called_once()
    mock_client.views_update.assert_called_once()
    command.jira.getSprintsInBoard.assert_called_once_with(selected_board_id)

# def test_runSprintReport(command, body_with_all_inputs):
#     mock_ack = MagicMock()
#     mock_client = MagicMock()
#
#     command.runSprintReport(mock_ack, body_with_all_inputs, mock_client)
