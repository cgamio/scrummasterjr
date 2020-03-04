from requests.auth import HTTPBasicAuth
import requests
import logging
import re

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
            return "Looks like there's an issue with my connection. I've logged an error"

    def __getSprintMetrics(self, id):
        raise Exception("This function hasn't been implemented yet!")

        return response

    def getSprintMetricsCommand(self, message):
        sprintid = re.search('sprint metrics ([0-9]+)', message).group(1)

        try:
            response = self.__getSprintMetrics(sprintid)
        except BaseException as e:
            logging.error(f"There was an error generating sprint metrics for sprint {sprintid}\n{str(e)}")
            return "Sorry, I had trouble getting metrics for that sprint. I've logged an error"

        return response


    def getCommandsRegex(self):
        return {
            'test jira': self.testConnectionCommand,
            'sprint metrics [0-9]+': self.getSprintMetricsCommand
        }

    def getCommandDescriptions(self):
        return {
            'test jira': 'tests my connection to jira',
            'sprint metrics [sprint-id]': 'get metrics for a given sprint'
        }
