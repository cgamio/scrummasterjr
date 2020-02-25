from slackeventsapi import SlackEventAdapter
import slack
import os
import re
import random

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = slack.WebClient(slack_bot_token)

def say_hello(message):
    responses = ["Hello there!",
                 "It's a pleasure to meet you! My name is Scrum Master Jr.",
                 "Oh! Sorry, you startled me. I didn't see you there.",
                 "Hi!",
                 "Howdy!",
                 "Aloha!",
                 "Hola!",
                 "Bonjour!"
                ]

    slack_client.chat_postMessage(channel=message["channel"], text=random.choice(responses))

@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    message = event_data["event"]

    if message.get("subtype") is None:
        text = message.get("text")
        if re.search('h(ello|i)', text):
            say_hello(message)

slack_events_adapter.start(port=3000)
