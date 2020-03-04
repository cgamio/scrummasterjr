from requests.auth import HTTPBasicAuth
import requests
import logging
import re
import json

class Jira:
    __auth = None
    __token = None
    __url = None
    __greenhopper_url = None
    __agile_url = None

    def __makeRequest(self, verb, url, params=None):
        response = requests.request(verb, url, headers={ 'Accept': 'application/json' }, auth=self.__auth, params=params)
        if response.status_code == 200:
            return(json.loads(response.text))
        else:
            logging.error(response.text)
            return(False)

    def __init__(self, host, user, token):
        self.__host = host
        self.__auth = HTTPBasicAuth(user, token)

        self.__url = f"https://{self.__host}/rest/api/latest/"
        self.__agile_url = f"https://{self.__host}/rest/agile/latest/"
        self.__greenhopper_url = f"https://{self.__host}/rest/greenhopper/latest/"

    def __testConnection(self):
        url = f"{self.__url}/myself"

        response = self.__makeRequest('GET', url)

        return response

    def testConnectionCommand(self, message):
        response = self.__testConnection()

        if response == False:
            logging.error(f"Error with Jira connection: {response}")
            return "Looks like there's an issue with my connection. I've logged an error"
        else:
            return "My connection to Jira is up and running!"

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
