import pytest
from scrummasterjr import app
from unittest.mock import MagicMock, call, patch

def test_help_no_set():
    # Test getting help with no command sets
    expected_response = "These are the things I know how to respond to:\nhello - random greeting"

    app.commandsets = []

    response = app.get_help("help")
    assert response == expected_response

def test_help_mock_set():
    # Test getting help with a Mock command set
    set = MagicMock()
    set.getCommandDescriptions.return_value = {"some command": "does a test thing"}

    app.commandsets = [set]

    expected_response = "These are the things I know how to respond to:\nhello - random greeting\nsome command - does a test thing"

    response = app.get_help("help")

    set.getCommandDescriptions.assert_called()
    assert response == expected_response

@pytest.mark.parametrize('message , expected_response', [
    ({'text':'help', 'channel': '1234'},
     "These are the things I know how to respond to:\nhello - random greeting\nsome command - does a test thing"
    ),
    ({'text':'asldkfjaslkdjhfa', 'channel': '1234'},
     "I'm sorry, I don't understand you. Try asking me for `help`"
    )
])
def test_handle_mention(message, expected_response):
    mock_say = MagicMock()

    app.handle_message(message, mock_say.say)

    mock_say.say.assert_called_with(expected_response)

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
    mock_say = MagicMock()
    def side_effect(*args, **kwargs):
        assert args[0] in hello_responses

    mock_say.side_effect = side_effect

    app.handle_message({'text':'hello',
    'channel': '1234'}, mock_say.say)

def test_handle_response_error():
    message = {'subtype': None, 'text':'This was a message that generated and error', 'channel': '1234'}
    def throw_error(message_arg):
        assert message['text'] == message_arg
        return ('This is a user-facing error message', 'This is an admin error notification.')

    mock_say = MagicMock()

    app.slack_error_channel = '4321'

    app.handle_response(throw_error, message, mock_say.say)

    mock_say.say.assert_called_with('This is a user-facing error message')

    app.chat_postMessage.assert_has_calls([
        call(channel='4321', text="<!here> This is an admin error notification.\nMessage that generated this error:\n```{'subtype': None, 'text': 'This was a message that generated and error', 'channel': '1234'}```"),
        call(channel='1234', text='This is a user-facing error message')
    ])
