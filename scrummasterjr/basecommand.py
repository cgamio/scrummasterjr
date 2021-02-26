class BaseCommand:

    def __init__ (self, regex, description):
        self.regex = regex
        self.description = description

    def getCommandsRegex(self):
        return self.regex

    def getCommandDescriptions(self):
        return self.descriptions
