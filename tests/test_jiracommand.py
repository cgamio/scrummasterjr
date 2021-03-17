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
