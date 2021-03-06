import pytest
from scrummasterjr.jira import Jira
from scrummasterjr.error import ScrumMasterJrError
from unittest.mock import MagicMock, patch
import json
import re
from fixtures import *

jira = Jira(jira_test_instance, " ", " ")

@patch('scrummasterjr.jira.requests')
def test_testConnection(mock_requests):

    def request_side_effect(verb, url, *args, **kwargs):
        if 'myself' in url:
            return MagicMock(**okRequestResponse({"data": "a-okay"}))

    mock_requests.request.side_effect = request_side_effect

    jira.testConnection()
    mock_requests.request.assert_called_once()

@patch('scrummasterjr.jira.requests')
@pytest.mark.parametrize('message, sprint_get_response, report_get_response, board_get_response,  expected_response', [
    ('sprint metrics 1234', badRequestResponse('No Sprint Found!'), {}, {}, ScrumMasterJrError("I could not find sprint with id 1234. Please check your arguments again. Are you using the right command for your jira instance? Ask me for `help` for more information")),
    ('sprint metrics abcd', {}, {}, {}, "Sorry, I don't see a valid sprint number there"),
    ('sprint metrics 1234', {}, badRequestResponse('No Board Found!'), {},  ScrumMasterJrError("I could not find sprint with id 1234. Please check your arguments again. Are you using the right command for your jira instance? Ask me for `help` for more information")),
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

    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            jira.getSprintMetricsCommand(message)
    else:
        response = jira.getSprintMetricsCommand(message)

        if isinstance(expected_response,dict):
            strip_blockqoutes = re.compile('```([^`]*)```', re.MULTILINE)
            result_dict = json.loads(strip_blockqoutes.match(response['text']).group(1))

            assert result_dict == expected_response
        else:
            assert response == {'text': expected_response}

@patch('scrummasterjr.jira.requests')
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
        with pytest.raises(ScrumMasterJrError):
            assert jira.getAverageVelocity('1234', sprint_id) == expected_response
    else:
        assert jira.getAverageVelocity('1234', sprint_id) == expected_response

@patch('scrummasterjr.jira.requests')
@pytest.mark.parametrize('sprint_id, sprint_get_response, report_get_response, board_get_response, velocity_get_response, expected_response', [
    ('5432', badRequestResponse('No Sprint Found!'), {}, {}, {}, ScrumMasterJrError("Sorry, I had trouble generating a report for that sprint. I've logged an error")),
    ('5432', valid_sprint_response, {}, badRequestResponse('No Report Found!'), {}, ScrumMasterJrError("Sorry, I had trouble generating a report for that sprint. I've logged an error")),
    ('1234', valid_sprint_response, okRequestResponse(normal_sprint_data['sprint_report_response']),  badRequestResponse('No Board Found!'), okRequestResponse(report_velocity_response['velocity_get_response']), ScrumMasterJrError("Sorry, I had trouble generating a report for that sprint. I've logged an error")),
    ('1234', valid_sprint_response, okRequestResponse(no_goals_or_dates_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), ScrumMasterJrError("Sorry, I had trouble generating a report for that sprint. I've logged an error")),
    ('1234', valid_sprint_response, okRequestResponse(no_sprint_number_sprint_data['sprint_report_response']),  valid_board_response, okRequestResponse(report_velocity_response['velocity_get_response']), ScrumMasterJrError("Sorry, I had trouble generating a report for that sprint. I've logged an error")),
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
        with pytest.raises(ScrumMasterJrError):
            jira.generateAllSprintReportData(sprint_id)
    else:
        assert jira.generateAllSprintReportData(sprint_id) == expected_response

@pytest.mark.parametrize('sprint_report_data, expected_response', [
    (valid_report, valid_google_form_url),
    ({}, Exception('Unable to generate Google Form URL, expected keys missing'))
])
def test_generateGoogleFormURL(sprint_report_data, expected_response):

    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            jira.generateGoogleFormURL(sprint_report_data)
    else:
        assert jira.generateGoogleFormURL(sprint_report_data) == expected_response

@pytest.mark.parametrize('sprint_report_data, expected_response', [
    ({}, Exception("Unable to generate a Notion Replacement Dictionary, keys not found")),
    (valid_report, validNotionReplacementDictionary)
])
def test_generateNotionReplacementDictionary(sprint_report_data,  expected_response):
    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            jira.generateNotionReplacementDictionary(sprint_report_data)
    else:

        actual_response = jira.generateNotionReplacementDictionary(sprint_report_data)

        for key in sorted(expected_response):
            assert expected_response[key] == actual_response[key]

@pytest.mark.parametrize('sprint_report_data, expected_response', [
    ({}, Exception("Unable to generate a Notion Replacement Dictionary, keys not found")),
    (valid_report, validNextSprintNotionReplacementDictionary)
])
def test_generateNextSprintNotionReplacementDictionary(sprint_report_data,  expected_response):
    if isinstance(expected_response, Exception):
        with pytest.raises(ScrumMasterJrError):
            jira.generateNextSprintNotionReplacementDictionary(sprint_report_data)
    else:

        actual_response = jira.generateNextSprintNotionReplacementDictionary(sprint_report_data)

        for key in sorted(expected_response):
            assert expected_response[key] == actual_response[key]

@pytest.mark.parametrize('issue_numbers, expected_response', [
    (normal_sprint_data['expected_response']['issue_keys']['completed'], f"https://{jira_test_instance}/issues/?jql=issueKey%20in%20(NORMAL-1%2CNORMAL-2%2CNORMAL-3%2CNORMAL-4%2CNORMAL-5)"),
    ([], f"https://{jira_test_instance}/issues/?jql=issueKey%20in%20()")
])
def test_generateJiraIssueLink(issue_numbers, expected_response):
    assert jira.generateJiraIssueLink(issue_numbers) == expected_response


@patch('scrummasterjr.jira.NotionPage')
@pytest.mark.parametrize('next_sprint_report, notion_exception', [
    (True, None),
    (True, ScrumMasterJrError('Some Error')),
    (False, None),
    (False, ScrumMasterJrError('Some Error'))
])
def test_updateNotionPage(mock_notion_page_class, next_sprint_report, notion_exception) :
    mock_notion_page = MagicMock()
    mock_notion_page_class.return_value = mock_notion_page

    mock_notion_page.searchAndReplace.side_effect = notion_exception
    notion_url = "https://www.notion.so/mediaos/some-test-document"

    if next_sprint_report:
        jira.updateNotionPage(notion_url, valid_report, valid_report)
    else:
        jira.updateNotionPage(notion_url, valid_report)

    mock_notion_page_class.assert_called_once_with(notion_url)
    mock_notion_page.searchAndReplace.assert_called_once()
