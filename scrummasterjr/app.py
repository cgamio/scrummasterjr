import os
import re
import random
import logging
import threading
import time

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

logging.basicConfig(
    format="[%(asctime)-15s] %(levelname)-8s %(module)-15s l:%(lineno)-4d msg: %(message)s",
    level=os.getenv('LOG_LEVEL', 'INFO')
)

from scrummasterjr.jira import Jira
from scrummasterjr.jiracommand import JiraCommand
from scrummasterjr.error import ScrumMasterJrError

# flask / bolt apps
flask_app = Flask(__name__)
app = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])
handler = SlackRequestHandler(app)

@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()

def dms_only(message, next, logger):
    channel_type = message.get('channel_type')

    if channel_type == "im":
        return next()

    logger.debug("This message was not a DM")

def no_bot_messages(message, next, logger):
    """Listener middleware which filters out messages from bots by checking 'bot_id'"""
    bot_id = message.get('bot_id')

    if bot_id is None:
        return next()

    logger.debug(f'Ignoring message from bot: {bot_id}')

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
    cds_jira = Jira(cds_jira_host, cds_jira_user, cds_jira_token)
    cds_jira_command = JiraCommand(cds_jira, "cds")
    commandsets.append(cds_jira_command)
except KeyError:
    logging.warning("Did not find CDS Jira Environment Variables. Continuing without registering that command set")

# Set up for Jira Commands
try:
    jira_host = os.environ["JIRA_HOST"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    jira = Jira(jira_host, jira_user, jira_token)
    jiraCommand = JiraCommand(jira)
    commandsets.append(jiraCommand)
except KeyError:
    logging.warning("Did not find Jira Environment Variables. Continuing without registering that command set")

def handle_response(function, message, say):
    """Executes a command and forwards the response back to the user

    Args:
        function: function reference - the function that should be called
        message: string - the message that triggered this events
    """
    try:
        function_response = function(message)
    except ScrumMasterJrError as smjrerr:
        if slack_error_channel:
            errortext = f"<!here> {smjrerr.admin_message}\nMessage that generated this error:\n```{message}```"
            app.client.chat_postMessage(channel=slack_error_channel, text=errortext)

        function_response = smjrerr.user_message
        say(smjrerr.user_message)

    say(function_response)

def response_timer(handle_response_thread, message, say):
    """Ensures that the user always gets some response within 3 seconds

    Args:
        handle_response_thread: thread reference - the main execution thread. If this thread is still alive after 3 seconds, we want to give the user a heads up
        message: slack message - the message that triggered the main execution thread (so we know where to post the follow up message)
    """
    time.sleep(3)
    if handle_response_thread.isAlive():
        say("Hmmmm... That's a tough one. Let me think about it for a minute")

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

    return(random.choice(responses))

def get_help(text):
    """Get help information for all of the command sets and share that with the user

    Args:
        text: string - the text the user sent that triggered this event (not used in this case, just meant to be consistent with all commands)

    Returns:
        dictionary - Help text on all the commands that are currently registered with the bot
    """
    response = "These are the things I know how to respond to:\nhello - random greeting"
    for set in commandsets:
        for command in set.getCommandDescriptions().keys():
            response = f"{response}\n{command} - {set.getCommandDescriptions()[command]}"
        response = f"{response}\n"

    return(response.strip())

@app.event("app_mention")
@app.event("message", middleware=[dms_only, no_bot_messages])
def handle_message(event, say):

    text = event["text"]

    if re.search('h(ello|i)', text):
        handle_response(say_hello, event, say)
        return
    if re.search('help', text):
        handle_response(get_help, event, say)
        return
    for set in commandsets:
        for regex in set.getCommandsRegex().keys():
            if re.search(regex, text):
                thread = threading.Thread(target=handle_response, args=(set.getCommandsRegex()[regex], event, say))
                timer_thread = threading.Thread(target=response_timer, args=(thread, event, say))
                thread.start()
                timer_thread.start()
                return

    say("I'm sorry, I don't understand you. Try asking me for `help`")

@app.event({"type": "message"})
def just_ack(ack, logger):
    """This listener handles all uncaught message events and just acks"""
    logger.debug('ignored message.')
    ack()

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/health")
def healthcheck():
    """A simple health endpoint that returns 200 as long as the app is running"""
    return "Up and Running!", 200

if __name__ == '__main__':
    debug = True if 'prod' not in str(os.getenv('ENV')) else False
    flask_app.run(host='0.0.0.0', port=8081, debug=debug)
