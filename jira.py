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

    def __calculateSprintMetrics(self, sprint_report):
        points = {
            "committed": 0,
            "completed": 0,
            "planned_completed": 0,
            "unplanned_completed": 0,
            "feature_completed": 0,
            "optimization_completed": 0,
            "not_completed": 0,
            "removed": 0
        }

        items = {
            "committed": 0,
            "completed": 0,
            "planned_completed": 0,
            "unplanned_completed": 0,
            "stories_completed": 0,
            "unplanned_stories_completed": 0,
            "bugs_completed": 0,
            "unplanned_bugs_completed": 0,
            "not_completed": 0,
            "removed": 0
        }

        issue_keys = {
            "committed": [],
            "completed": [],
            "incomplete": [],
            "removed": []
        }

        feature_work = ["Story", "Design", "Spike"]
        optimization = ["Optimization"]
        bug = ["Bug"]
        ignore = ["Task", "Epic"]

        # Completed Work
        for completed in sprint_report["contents"]["completedIssues"]:
            issue_keys["completed"].append(completed["key"])

            # Short-circuit for things we don't track
            if completed["typeName"] in ignore:
                continue

            try:
                issue_points_original = int(completed["estimateStatistic"]["statFieldValue"]["value"])
            except:
                issue_points_original = 0

            try:
                issue_points = int(completed["currentEstimateStatistic"]["statFieldValue"]["value"])
            except:
                issue_points = 0

            points["completed"] += issue_points
            items["completed"] += 1

            unplanned = False
            if completed["key"] in sprint_report["contents"]["issueKeysAddedDuringSprint"].keys():
                unplanned = True
                points["unplanned_completed"] += issue_points_original
                items["unplanned_completed"] += 1
            else:
                issue_keys["committed"].append(completed["key"])
                points["committed"] += issue_points_original
                items["committed"] += 1
                points["planned_completed"] += issue_points
                items["planned_completed"] += 1
                if issue_points_original < issue_points:
                    points["unplanned_completed"] += issue_points-issue_points_original

            # Story
            if completed["typeName"] == "Story":
                items["stories_completed"] += 1
                if unplanned:
                    items["unplanned_stories_completed"] += 1

            # Story / Design / Spike (Feature Work)
            if completed["typeName"] in feature_work:
                points["feature_completed"] += issue_points

            # Optimization
            if completed["typeName"] in optimization:
                points["optimization_completed"] += issue_points

            # Bugs
            if completed["typeName"] in bug:
                items["bugs_completed"] += 1
                if unplanned:
                    items["unplanned_bugs_completed"] += 1


        # Incomplete Work
        for incomplete in sprint_report["contents"]["issuesNotCompletedInCurrentSprint"]:

            issue_keys["incomplete"].append(incomplete["key"])

            # Short-circuit for things we don't track
            if incomplete["typeName"] in ignore:
                continue

            try:
                issue_points = int(incomplete["currentEstimateStatistic"]["statFieldValue"]["value"])
            except:
                issue_points = 0

            points["not_completed"] += issue_points
            items["not_completed"] += 1

            if incomplete["key"] not in sprint_report["contents"]["issueKeysAddedDuringSprint"].keys():
                issue_keys["committed"].append(incomplete["key"])
                points["committed"] += issue_points
                items["committed"] += 1

        # Removed Work
        for removed in sprint_report["contents"]["puntedIssues"]:

            issue_keys["removed"].append(removed["key"])

            # Short-circuit for things we don't track
            if removed["typeName"] in ignore:
                continue

            try:
                issue_points = int(removed["currentEstimateStatistic"]["statFieldValue"]["value"])
            except:
                issue_points = 0

            if removed["key"] not in sprint_report["contents"]["issueKeysAddedDuringSprint"].keys():
                points["committed"] += issue_points
                items["committed"] += 1
                issue_keys["committed"].append(removed["key"])

            points["removed"] += issue_points
            items["removed"] += 1

        return {
            "points" : points,
            "items" : items,
            "issue_keys": issue_keys
        }

    def __getSprintReport(self, sprint_id):
        # Get Jira Sprint Object (including Board reference) from Sprint ID
        sprint = self.__makeRequest('GET', f"{self.__agile_url}sprint/{sprint_id}")
        if sprint == False:
            raise Exception(f"Could not find sprint with id {sprint_id}")

        sprint_report = self.__makeRequest('GET',f"{self.__greenhopper_url}rapid/charts/sprintreport?rapidViewId={sprint['originBoardId']}&sprintId={sprint_id}")
        if sprint_report == False:
            raise Exception(f"Could not find report for sprint {sprint_id} on board {sprint['board_id']}")

        return sprint_report

    def getSprintMetricsCommand(self, message):
        sprintid = re.search('sprint metrics ([0-9]+)', message).group(1)

        try:
            sprint_report = self.__getSprintReport(sprintid)
            metrics = self.__calculateSprintMetrics(sprint_report)

        except BaseException as e:
            logging.error(f"There was an error generating sprint metrics for sprint {sprintid}\n{str(e)}")
            return "Sorry, I had trouble getting metrics for that sprint. I've logged an error"

        metrics_text = json.dumps(metrics, sort_keys=True, indent=4, separators=(",", ": "))
        return f"```{metrics_text}```"

    def getSprintReportCommand(self, message):
        sprintid = re.search('sprint report ([0-9]+)', message).group(1)

        try:
            sprint_report = self.__getSprintReport(sprintid)
            metrics = self.__calculateSprintMetrics(sprint_report)
            
        except BaseException as e:
            logging.error(f"There was an error generating sprint metrics for sprint {sprintid}\n{str(e)}")
            return "Sorry, I had trouble getting metrics for that sprint. I've logged an error"

        return "A dummy report"

    def getCommandsRegex(self):
        return {
            'test jira': self.testConnectionCommand,
            'sprint metrics [0-9]+': self.getSprintMetricsCommand,
            'sprint report [0-9]+': self.getSprintReportCommand
        }

    def getCommandDescriptions(self):
        return {
            'test jira': 'tests my connection to jira',
            'sprint metrics [sprint-id]': 'get metrics for a given sprint',
            'sprint report [sprint-id]': 'get a quick sprint report for a given sprint'
        }
