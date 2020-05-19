import pytest
import scrum_master_jr
from unittest.mock import MagicMock

@pytest.fixture
def client():
    with scrum_master_jr.app.test_client() as client:
        yield client

def test_healthcheck(client):
    rv = client.get('/health')

    assert 200 is rv.status_code

def test_help_no_set():
    # Test getting help with no command sets
    default_response = {'text': "These are the things I know how to respond to:\nhello - random greeting"}

    scrum_master_jr.commandsets = []

    response = scrum_master_jr.get_help("help")
    assert response == default_response

def test_help_mock_set():
    # Test getting help with a Mock command set
    set = MagicMock()
    set.getCommandDescriptions.return_value = {"some command": "does a test thing"}

    scrum_master_jr.commandsets = [set]

    expected_response = {'text': "These are the things I know how to respond to:\nhello - random greeting\nsome command - does a test thing"}
    response = scrum_master_jr.get_help("help")

    set.getCommandDescriptions.assert_called()
    assert response == expected_response

@pytest.mark.parametrize('message , expected_response', [
    ({'event': {'subtype': None, 'text':'help', 'channel': '1234'}},
     {'channel':'1234', 'text':"These are the things I know how to respond to:\nhello - random greeting\nsome command - does a test thing"}
    ),
    ({'event': {'subtype': None, 'text':'asldkfjaslkdjhfa', 'channel': '1234'}},
     {'channel':'1234', 'text':"I'm sorry, I don't understand you. Try asking me for `help`"}
    )
])
def test_handle_mention(message, expected_response):
    mock_slack_client = MagicMock()
    scrum_master_jr.slack_client = mock_slack_client

    scrum_master_jr.handle_mention(message)

    mock_slack_client.chat_postMessage.assert_called_with(**expected_response)

hello_responses = ["Hello there!",
             "It's a pleasure to meet you! My name is Scrum Master Jr.",
             "Oh! Sorry, you startled me. I didn't see you there.",
             "Hi!",
             "Howdy!",
             "Aloha!",
             "Hola!",
             "Bonjour!"
            ]

def test_handle_mention_hello():
    mock_slack_client = MagicMock()
    def side_effect(*args, **kwargs):
        assert kwargs['text'] in hello_responses

    mock_slack_client.side_effect = side_effect
    scrum_master_jr.slack_client = mock_slack_client

    scrum_master_jr.handle_mention({'event': {'subtype': None, 'text':'hello', 'channel': '1234'}})

    mock_slack_client.chat_postMessage.assert_called_once()
