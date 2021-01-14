import pytest
from unittest.mock import MagicMock, patch
import logging

@pytest.fixture(scope='function')
def app(setup_environment):
    with patch('slack_bolt.App') as mock:
        from scrummasterjr import app
        app.client = MagicMock()
    yield app

@pytest.fixture()
def setup_environment(monkeypatch):
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'xoxb-valid')
    monkeypatch.setenv('SLACK_SIGNING_SECRET', 'test-signing-secret')
    monkeypatch.setenv('JIRA_HOST', 'test-jira-host')
    monkeypatch.setenv('JIRA_USER', 'test-jira-user')
    monkeypatch.setenv('JIRA_TOKEN', 'test-jira-token')
    monkeypatch.setenv('NOTION_TOKEN', 'test-notion-token')
