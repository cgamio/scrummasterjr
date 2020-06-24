from slackeventsapi import SlackEventAdapter
import slack
import os
import re
import random
from flask import Flask, jsonify, request
import logging
logging.basicConfig(format='%(message)s')
import threading
import time

from jira import Jira

app = Flask(__name__)

@app.route("/health")
def healthcheck():
    """A simple health endpoint that returns 200 as long as the app is running"""
    return "Up and Running!", 200

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = slack.WebClient(slack_bot_token)

# Get Channel to post error messages to
try:
    slack_error_channel = os.environ["SLACK_ERROR_CHANNEL"]
except KeyError:
    slack_error_channel = None

commandsets = []

# Set up for CDS Jira Commands (if configured)
try:
    cds_jira_host = os.environ["CDS_JIRA_HOST"]
    cds_jira_user = os.environ["CDS_JIRA_USER"]
    cds_jira_token = os.environ["CDS_JIRA_TOKEN"]
    cds_jira = Jira(cds_jira_host, cds_jira_user, cds_jira_token, "cds")
    commandsets.append(cds_jira)
except KeyError:
    logging.warning("Did not find CDS Jira Environment Variables. Continuing without registering that command set")

# Set up for Jira Commands
try:
    jira_host = os.environ["JIRA_HOST"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    jira = Jira(jira_host, jira_user, jira_token)
    commandsets.append(jira)
except KeyError:
    logging.warning("Did not find Jira Environment Variables. Continuing without registering that command set")

def say_hello(text):
    """ A basic hello interaction

    Args:
        text - the text the user sent that triggered this event (not used in this case, just meant to be consistent with all commands)

    Returns:
        A random "hello" response to be polite to users who greet the bot
    """
    responses = ["Hello there!",
                 "It's a pleasure to meet you! My name is Scrum Master Jr.",
                 "Oh! Sorry, you startled me. I didn't see you there.",
                 "Hi!",
                 "Howdy!",
                 "Aloha!",
                 "Hola!",
                 "Bonjour!"
                ]

    return {'text': random.choice(responses)}

def get_help(text):
    """Get help information for all of the command sets and share that with the user

    Args:
        text - the text the user sent that triggered this event (not used in this case, just meant to be consistent with all commands)

    Returns:
        Help text on all the commands that are currently registered with the bot
    """
    response = "These are the things I know how to respond to:\nhello - random greeting"
    for set in commandsets:
        for command in set.getCommandDescriptions().keys():
            response = f"{response}\n{command} - {set.getCommandDescriptions()[command]}"
        response = f"{response}\n"

    return {'text': response.strip()}

def handle_response(function, message):
    """Executes a command and forwards the response back to the user

    Args:
        function - the function that should be called
        message - the message that triggered this events
    """
    function_response = function(message['text'])
    if type(function_response) is tuple:
        if slack_error_channel:
            response, errortext = function_response
            errormessage={
                'channel': slack_error_channel,
                'text': f"<!here> {errortext}\nMessage that generated this error:\n```{message}```"}
            slack_client.chat_postMessage(**errormessage)

            function_response = response

    function_response['channel'] = message['channel']
    slack_client.chat_postMessage(**function_response)

def response_timer(handle_response_thread, message):
    time.sleep(3)
    if handle_response_thread.isAlive():
        slow_execution_message={
            'channel': message['channel'],
            'text': "Hmmmm... That's a tough one. Let me think about it for a minute"}
        slack_client.chat_postMessage(**slow_execution_message)

@slack_events_adapter.on("message")
def handle_message(event_data):
    """Handles all messages

    Args:
        event-data - the slack event data that triggered this adapter (contains the message and other metadata)
    """
    if event_data['event']['channel_type'] == 'im':
        # Treat DM's as @mentions
        handle_mention(event_data)

@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    """Handles slack @mentions

    Args:
        event-data - the slack event data that triggered this adapter (contains the message and other metadata)
    """
    message = event_data["event"]

    if 'bot_id' in message.keys():
        # We don't want to respond to other bots, so bail
        return

    if message.get("subtype") is None:
        text = message.get("text")

        if re.search('h(ello|i)', text):
            handle_response(say_hello, message)
            return
        if re.search('help', text):
            handle_response(get_help, message)
            return
        for set in commandsets:
            for regex in set.getCommandsRegex().keys():
                if re.search(regex, text):
                    thread = threading.Thread(target=handle_response, args=(set.getCommandsRegex()[regex], message))
                    timer_thread = threading.Thread(target=response_timer, args(thread, message))
                    thread.start()
                    timer_thread.start()
                    return

        slack_client.chat_postMessage(channel=message["channel"], text="I'm sorry, I don't understand you. Try asking me for `help`")

# Start the server on port 80
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)
