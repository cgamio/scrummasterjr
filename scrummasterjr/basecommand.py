class BaseCommand:

    def __init__ (self, regex, descriptions):
        self.regex = regex
        self.descriptions = descriptions

    def getCommandsRegex(self):
        return self.regex

    def getCommandDescriptions(self):
        return self.descriptions
