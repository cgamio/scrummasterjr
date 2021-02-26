import pytest
from scrummasterjr.jiracommand import JiraCommand
from scrummasterjr.error import ScrumMasterJrError
from unittest.mock import MagicMock, patch, call
from fixtures import *

jiracommand = JiraCommand(None)

@pytest.mark.parametrize('jira_response, expected_response', [
    (200, "My connection to Jira is up and running!"),
    (None, "Looks like there's an issue with my connection. I've logged an error")
])
def test_testConnectionCommand(jira_response, expected_response):
    mock_jira = MagicMock()
    mock_jira.testConnection.return_value = jira_response
    jiracommand.jira = mock_jira

    response = jiracommand.testConnection(None)

    assert response == expected_response

# Input / Output Permutations
# Single Sprint (valid)
# Single Sprint (error)
# Multi-Sprint (valid)
# Multi-Sprint (error)
# Multi-Sprint w/ Notion (successful)
# Multi-Sprint w/ Notion (error)

# Function Calls to Mock
# self.jira.generateAllSprintReportData
# self.jira.updateNotionPage
# self.jira.generateGoogleFormURL

# @pytest.mark.parametrize('slack_event,  notion_case, expected_response', [
#     ('sprint report 5432', badRequestResponse('No Sprint Found!'), {}, {}, {}, False, ScrumMasterJrError({'text': "Sorry, I had trouble generating a report for that sprint. I've logged an error"})),
#     ('sprint report 1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), False, valid_blocks),
#     ('sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), valid_notion_case, valid_notion_blocks),
#     ('sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), error_notion_case, ScrumMasterJrError(notion_error_blocks, ""))
# ])

bad_sprint_error = ScrumMasterJrError('Something Bad', 'Something Specifically Bad')
google_form_url_error = ScrumMasterJrError('Something Bad', 'Something Specifically Bad')
bad_notion_error = ScrumMasterJrError(notion_error_blocks)
#
# @pytest.mark.parametrize('slack_event, sprint_data_input, sprint_data_response, generate_google_form_url_response, expected_response', [
#     ({'text': 'sprint report 5432'}, '5432', bad_sprint_error, None, bad_sprint_error),
#     ({'text': 'sprint report 1234'}, '1234', valid_report, valid_google_form_url, valid_blocks)
#     ])
# def test_getSprintReport_Single_Sprint(slack_event, sprint_data_input, sprint_data_response, generate_google_form_url_response, expected_response):
#     mock_jira = MagicMock()
#     jiracommand.jira = mock_jira
#
#     mock_jira.generateAllSprintReportData.return_value = sprint_data_response
#     if isinstance(sprint_data_response, Exception):
#         mock_jira.generateAllSprintReportData.side_effect = sprint_data_response
#
#     mock_jira.generateGoogleFormURL.return_value = generate_google_form_url_response
#     if isinstance(generate_google_form_url_response, Exception):
#         mock_jira.generateGoogleFormURL.side_effect = generate_google_form_url_response
#
#     if isinstance(expected_response, Exception):
#         with pytest.raises(ScrumMasterJrError):
#             jiracommand.getSprintReport(slack_event)
#     else:
#         assert jiracommand.getSprintReport(slack_event) == expected_response
#
#     mock_jira.generateAllSprintReportData.assert_called_once_with( sprint_data_input)
#
@pytest.mark.parametrize('slack_event, all_sprint_data_input, all_sprint_data_response, notion_url, update_notion_page_response, generate_google_form_url_response, expected_response', [
    ({'text': 'sprint report 5432'}, ['5432'], [bad_sprint_error], None, None, None, bad_sprint_error),
    ({'text': 'sprint report 1234'}, ['1234'], [valid_report], None, None, valid_google_form_url, valid_blocks),
    ({'text': 'sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document'}, ['1234', '5678'], [valid_report, valid_report], "https://www.notion.so/mediaos/some-test-document", valid_notion_case, valid_google_form_url, valid_notion_blocks),
    ({'text': 'sprint report 1234 5678 https://www.notion.so/mediaos/some-test-document'}, ['1234', '5678'], [valid_report, valid_report], "https://www.notion.so/mediaos/some-test-document", bad_notion_error, valid_google_form_url, bad_notion_error),
])
def test_getSprintReport(slack_event, all_sprint_data_input, all_sprint_data_response, notion_url, update_notion_page_response, generate_google_form_url_response, expected_response):

    mock_jira = MagicMock()
    jiracommand.jira = mock_jira

    if isinstance(update_notion_page_response, Exception):
        mock_jira.updateNotionPage.return_value = update_notion_page_response
    else:
        mock_jira.updateNotionPage.return_value = None

    mock_jira.generateAllSprintReportData.side_effect = all_sprint_data_response

    if generate_google_form_url_response:
        mock_jira.generateGoogleFormURL.return_value = generate_google_form_url_response

        if isinstance(generate_google_form_url_response, Exception):
            mock_jira.generateGoogleFormURL.side_effect = lambda x: exec(f"raise(ScrumMasterJrError('An Error!'))")

    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            jiracommand.getSprintReport(slack_event)
    else:
        assert jiracommand.getSprintReport(slack_event) == expected_response

    if all_sprint_data_response:
        mock_jira.generateAllSprintReportData.assert_has_calls(map(call, all_sprint_data_input))

    if update_notion_page_response and not isinstance(update_notion_page_response, Exception):
        mock_jira.updateNotionPage.assert_called_once_with(notion_url, *all_sprint_data_response)
