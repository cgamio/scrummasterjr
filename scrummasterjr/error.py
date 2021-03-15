class ScrumMasterJrError(Exception):
    """Raised when we have an application error that we want to pass information to the user, and provide some additional context to administrators

    Attributes:
        message -- message to pass back along to the user
        admin_message -- message to forward to administrators for contex
    """

    def __init__(self, message, admin_message=None):
        super().__init__(message)
        self.user_message = message
        self.admin_message = admin_message
