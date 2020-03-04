from requests.auth import HTTPBasicAuth
import requests
import logging

class Jira:
    __auth = None
    __token = None
    __url = None

    __headers = { 'Accept': 'application/json' }

    def __init__(self, host, user, token):
        self.__host = host
        self.__auth = HTTPBasicAuth(user, token)

        self.__url = f"https://{self.__host}/rest/api/latest/"

    def __testConnection(self):
        url = f"{self.__url}/myself"

        response = requests.request('GET', url, headers=self.__headers, auth=self.__auth)

        return response

    def testConnectionCommand(self, message):
        response = self.__testConnection()

        if response.status_code == 200:
            return "My connection to Jira is up and running!"
        else:
            logging.error(f"Error with Jira connection: {response}")
            return "Looks like there's an issue with my connection..."

    def getCommandsRegex(self):
        return {
            'test jira': self.testConnectionCommand
        }

    def getCommandDescriptions(self):
        return {
            'test jira': 'tests my connection to jira'
        }
