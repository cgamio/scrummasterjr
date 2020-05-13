from slackeventsapi import SlackEventAdapter
import slack
import os
import re
import random
from flask import Flask, jsonify, request
import logging
logging.basicConfig(format='%(message)s')
import threading

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

# Set up for Jira Commands
jira_host = os.environ["JIRA_HOST"]
jira_user = os.environ["JIRA_USER"]
jira_token = os.environ["JIRA_TOKEN"]
jira = Jira(jira_host, jira_user, jira_token)

commandsets = [jira]

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
    response = function(message['text'])
    response['channel'] = message['channel']
    response = slack_client.chat_postMessage(**response)

@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    """Handles slack @mentions

    Args:
        event-data - the slack event data that triggered this adapter (contains the message and other metadata)
    """
    message = event_data["event"]

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
                    thread.start()
                    return

        slack_client.chat_postMessage(channel=message["channel"], text="I'm sorry, I don't understand you. Try asking me for `help`")

# Start the server on port 80
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)
