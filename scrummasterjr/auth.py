import os

from flask import current_app as app
from slackeventsapi.server import SlackServer


class SlackAuth(SlackServer):
    """ Uses Slack Events API Adapter SlackServer class to verify requests are coming from slack.

        Since we're running our own flask instance we just want to use the specific function
        verify_signature.

        https://github.com/slackapi/python-slack-events-api
    """

    def __init__(self):
        """ Sets the signing secret of the slack app.
            Each slack app would have its own signing secret.
        """
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    def verify_signature(self, request):
        """ Compares generated hash with slack's request signature
            to verify request originated from slack.

        Args:
            request: obj, Flask request object.

        Returns:
            Boolean
        """
        timestamp = request.headers.get('X-Slack-Request-Timestamp')
        signature = request.headers.get('X-Slack-Signature')

        is_authentic = super().verify_signature(timestamp, signature)
        app.logger.info(f'Request originated from slack: {is_authentic}')
        return is_authentic
