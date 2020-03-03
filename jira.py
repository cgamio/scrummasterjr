from requests.auth import HTTPBasicAuth
import requests

class Jira:
    __auth = None
    __token = None
    __url = None

    __headers = { 'Accept': 'application/json' }

    def __init__(self, host, user, token):
        self.__host = host
        self.__auth = HTTPBasicAuth(user, token)

        self.__url = f"https://{self.__host}/rest/api/latest/"

    def testConnection(self):
        url = f"{self.__url}/myself"

        response = requests.request('GET', url, headers=self.__headers, auth=self.__auth)

        return response
