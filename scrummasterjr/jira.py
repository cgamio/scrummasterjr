from requests.auth import HTTPBasicAuth
import requests
import logging
import re
import json
from datetime import datetime
from scrummasterjr.notionpage import NotionPage

class Jira:
    __auth = None
    __token = None
    __url = None
    __greenhopper_url = None
    __agile_url = None
    __prefix = ''

    __regex = {}
    __descriptions = {}

    def __makeRequest(self, verb, url, params=None):
        """Wrapper for a simple HTTP request

            Args:
                verb: string - HTTP verb as string (ie. 'GET' or 'POST')
                url: string - URL to make HTTP requests against
                params: dictionary - Any request parameters to pass along (defaults to None)

            Returns:
                dictionary - A JSON represenatation of the response text, or False in the case of an error
        """
        response = requests.request(verb, url, headers={ 'Accept': 'application/json' }, auth=self.__auth, params=params)
        if response.status_code == 200:
            return(json.loads(response.text))
        else:
            logging.error(response.text)
            return(False)

    def __init__(self, host, user, token, prefix=False):
        self.__host = host
        self.__auth = HTTPBasicAuth(user, token)
        self.__prefix = f'{prefix} ' if prefix else ''

        self.__url = f"https://{self.__host}/rest/api/latest/"
        self.__agile_url = f"https://{self.__host}/rest/agile/latest/"
        self.__greenhopper_url = f"https://{self.__host}/rest/greenhopper/latest/"

        self.__regex = {
            f'test {self.__prefix}jira': self.testConnectionCommand,
            f'{self.__prefix}sprint metrics [0-9]+': self.getSprintMetricsCommand,
            f'{self.__prefix}sprint report [0-9]+': self.getSprintReportCommand,
            rf'{self.__prefix}sprint report (?P<sprint_id>[0-9]+)\s*((?P<next_sprint_id>[0-9]+)\s*<?(?P<notion_url>https://www.notion.so/[^\s>]+))?': self.getSprintReportCommand
        }

        self.__descriptions = {
            f'test {self.__prefix}jira': 'tests my connection to jira',
            f'{self.__prefix}sprint metrics [sprint-id]': 'get metrics for a given sprint',
            f'{self.__prefix}sprint report [sprint-id]': 'get a quick sprint report for a given sprint',
            f'{self.__prefix}sprint report [sprint-id] [next-sprint-id] [notion-url]': 'get a quick sprint report for a given sprint, the next sprint, and then update the given notion page'
        }

    def __testConnection(self):
        """Tests the connection to Jira by getting user data"""
        url = f"{self.__url}/myself"

        response = self.__makeRequest('GET', url)

        return response

    def testConnectionCommand(self, message):
        """Wrapper for Jira connection test functionality with user-friendly responses

        Args:
            message: string - the message from the user that initiated this command

        Returns:
            dictionary - A slack message response
        """
        response = self.__testConnection()
        text = "My connection to Jira is up and running!"
        if not response:
            logging.error(f"Error with Jira connection: {response}")
            text = "Looks like there's an issue with my connection. I've logged an error"

        return {'text': text}

    def __calculateSprintMetrics(self, sprint_report):
        """Given the data from a Jira sprint report, calculates sprint metrics

        Args:
            sprint_report: dictionary - the data from a Jira sprint reports

        Returns:
            dictionary - calculated metrics
        """
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
                points["unplanned_completed"] += issue_points
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

        meta = {
            "predictability": 0,
            "predictability_of_commitments": 0
        }

        if points['committed'] != 0:
            meta['predictability'] = int(points['completed']/points['committed']*100)
            meta['predictability_of_commitments'] = int(points['planned_completed']/points['committed']*100)
        else:
            # If a sprint has no points committed, we say the predictability is 0
            logging.warning('This sprint had no commitments, predictability is 0')

        return {
            "points" : points,
            "items" : items,
            "issue_keys": issue_keys,
            "meta": meta
        }

    def __getSprint(self, sprint_id):
        """Utility funtion to get sprint data from Jira

        Args:
            sprint_id: string - the id of a Jira sprint

        Returns:
            dictionary - A JSON encoded represenatation of the Jira sprint object
        """
        # Get Jira Sprint Object (including Board reference) from Sprint ID
        sprint = self.__makeRequest('GET', f"{self.__agile_url}sprint/{sprint_id}")
        if not sprint:
            raise Exception(f"Could not find sprint with id {sprint_id}")

        return sprint

    def __getBoard(self, board_id):
        """Utility funtion to get board data from Jira

        Args:
            board_id: string - the id of a Jira board

        Returns:
            dictionary - A JSON encoded represenatation of Jira board object
        """
        board = self.__makeRequest('GET', f"{self.__agile_url}board/{board_id}")
        if not board:
            raise Exception(f"Could not find boad with id {board_id}")

        return board

    def __getSprintReport(self, sprint_id, board_id):
        """Utility funtion to get sprint report data from Jira

        Args:
            sprint_id: string - the id of a Jira sprint
            board_id: string - the id of a Jira board

        Returns:
            dictionary - A JSON encoded represenatation of a Jira Sprint Report for the given sprint and board
        """
        sprint_report = self.__makeRequest('GET',f"{self.__greenhopper_url}rapid/charts/sprintreport?rapidViewId={board_id}&sprintId={sprint_id}")
        if not sprint_report:
            raise Exception(f"Could not find report for sprint {sprint_id} on board {board_id}")

        return sprint_report

    def getSprintMetricsCommand(self, message):
        """User-friendly wrapper for getting the metrics for a given sprint

        Args:
            message: string - the message from the user that initiated this command

        Returns:
            dictionary - A slack message response
        """
        try:
            sprintid = re.search('sprint metrics ([0-9]+)', message).group(1)
        except :
            logging.error(f"Did not find a sprint number in: '{message}'")
            return {'text': "Sorry, I don't see a valid sprint number there"}

        try:
            sprint = self.__getSprint(sprintid)
            sprint_report = self.__getSprintReport(sprintid, sprint['originBoardId'])
            metrics = self.__calculateSprintMetrics(sprint_report)

        except BaseException as e:
            logging.error(f"There was an error generating sprint metrics for sprint {sprintid}\n{e}")
            return {'text': "Sorry, I had trouble getting metrics for that sprint. I've logged an error"}

        metrics_text = json.dumps(metrics, sort_keys=True, indent=4, separators=(",", ": "))

        return {'text': f"```{metrics_text}```"}

    def __getJiraSprintReportData(self, sprint_report):
        """Utility funtion to parse general sprint information from a Jira sprint report

        Args:
            sprint_report: string - raw data from a Jira Sprint Report

        Returns:
            dictionary - relevant information parsed from the report
        """
        report = {}

        try:
            report['sprint_number'] = re.search(r'(?i)(S|Sprint )(?P<number>\d+)', sprint_report["sprint"]["name"]).group('number')
        except AttributeError:
            raise Exception(f"Could not find or parse sprint number from: '{sprint_report['sprint']['name']}'")

        try:
            report['sprint_start'] = sprint_report['sprint']['startDate']
            report['sprint_end'] = sprint_report['sprint']['endDate']
        except KeyError:
            # Every sprint doesn't have a start / end date
            logging.warning('This sprint does not have start and/or end dates')

        try:
            report['sprint_goals'] = sprint_report['sprint']['goal'].split("\n")
        except (AttributeError, KeyError):
            raise Exception(f"Could not find or parse sprint goal")

        return report

    def generateAllSprintReportData(self, sprint_id):
        """Congomerates all the data from different Jira reports into one holistic Sprint Report data-set

        Args:
            sprint_id: string - the id of a Jira sprint

        Returns:
            dictionary - the information necessary for creating an AgileOps Sprint Report
        """
        report = {}

        try:
            sprint = self.__getSprint(sprint_id)
            sprint_report = self.__getSprintReport(sprint_id, sprint['originBoardId'])
            report = self.__getJiraSprintReportData(sprint_report)
            report['issue_metrics'] = self.__calculateSprintMetrics(sprint_report)
            board = self.__getBoard(sprint['originBoardId'])
            report['project_name'] = board['location']['projectName']
            report['project_key'] = board['location']['projectKey']
            report['average_velocity'] = self.getAverageVelocity(sprint['originBoardId'], sprint_id)
        except BaseException as e:
            logging.error(f"There was an error generating a report sprint {sprint_id}\n{str(e)}")
            return {'text': "Sorry, I had trouble generating a report for that sprint. I've logged an error"}

        return report

    def getSprintReportCommand(self, message):
        """
        A user-friendly wrapper for getting sprint report data, having it displayed nicely, and optionally collect the next sprint's data to update a notion page.

        Args:
            message: string - containing the message from the user that initiated this commands

            Options:
            - 'sprint report 1234': Gets and prints the sprint report data for sprint 1234
            - 'spritn report 1234 5678 <https://notion.so/some-document': Gets and prints the sprint report data from sprint 1234, fetchs the data for sprint 5678 (assuming it's the next sprint) and updates the 'some-document' Notion page with that information

        Returns:
            dictionary - A slack response and an error message if applicable
        """

        error = None

        regex_result = re.search(r'sprint report (?P<sprint_id>[0-9]+)\s*((?P<next_sprint_id>[0-9]+)\s*<?(?P<notion_url>https://www.notion.so/[^\s>]+))?', message).groupdict()

        report_data = self.generateAllSprintReportData(regex_result['sprint_id'])
        if 'text' in report_data: return report_data

        blocks = []

        divider_block = {
    			"type": "divider"
    		}

        blocks.append({
    			"type": "image",
    			"title": {
    				"type": "plain_text",
    				"text": "Order Up!"
    			},
    			"image_url": "https://media.giphy.com/media/l1JojmmBMELYFKJc4/giphy.gif",
    			"alt_text": "Order Up!"
    		})
        blocks.append(divider_block)

        goals_string = '\n'.join(report_data['sprint_goals'])
        blocks.append({
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": f"*Project Name*: {report_data['project_name']}\n*Sprint {report_data['sprint_number']}*\n{goals_string}"
    			}
    		})

        blocks.append(divider_block)

        blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Metrics:*"
                }
                })

        sprint_metrics = []
        for type in ['items', 'points', 'meta']:
            type_block = {
        			"type": "section",
        			"text": {
        				"type": "mrkdwn",
        				"text": f"*{type}*"
        			}
        		}
            blocks.append(type_block)

            for metric in report_data['issue_metrics'][type].keys():
                sprint_metrics.append({
    					"type": "plain_text",
    					"text": f"{metric}"
    				})
                sprint_metrics.append({
    					"type": "plain_text",
    					"text": f"{report_data['issue_metrics'][type][metric]}"
    				})
                if len(sprint_metrics) > 8:
                    blocks.append({
                			"type": "section",
                			"fields": sprint_metrics
                    })
                    sprint_metrics = []

            if len(sprint_metrics) > 0:
                sprint_metrics_block = {
            			"type": "section",
            			"fields": sprint_metrics
                }
                blocks.append(sprint_metrics_block)
                sprint_metrics = []

        blocks.append(divider_block)

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{self.generateGoogleFormURL(report_data)}|Google Form URL>"
            }
            })

        if regex_result['notion_url'] and regex_result['next_sprint_id']:
            next_report_data = self.generateAllSprintReportData(regex_result['next_sprint_id'])
            if 'text' in next_report_data: return next_report_data

            result = self.updateNotionPage(regex_result['notion_url'], report_data, next_report_data)
            logging.error(f"Notion Page Update Result: {result}")

            blocks.append(divider_block)

            if result:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"There was an error updating the <{regex_result['notion_url']}|Notion Page>. I've notified my overlords and I'm sure they're looking into it"
                    }
                    })

                error = f"A user trying to update a Notion page got the following error. You might want to check / update the Notion token\n `{result}`"
            else:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{regex_result['notion_url']}|Notion Page> updated!"
                    }
                    })

        return ({"blocks": blocks}, error) if error else {"blocks": blocks}

    def updateNotionPage(self, notion_url, sprint_report_data, next_sprint_report_data=False):
        """Updates the notion page at the url with the sprint report data using a search / replace mechanism

        Args:
            notion_url: string - the URL to a notion page
            sprint_report_data: dictionary - AgileOps Sprint Report Data
            next_sprint_report_data: dictionary - AgileOps Sprint Report Data for the subsequent sprint (defaults to False if there is no next sprint)

        Returns:
            A BaseException if there was a problem
            boolean - False if everything ran smoothly
        """
        search_replace_dict = self.generateNotionReplacementDictionary(sprint_report_data)

        if next_sprint_report_data:
            search_replace_dict.update(self.generateNextSprintNotionReplacementDictionary(next_sprint_report_data))

        try:
            page = NotionPage(notion_url)
            logging.info(f"Notion Page: {page}")
            page.searchAndReplace(search_replace_dict)
        except BaseException as e:
            return e

        return False

    def getAverageVelocity(self, board_id, sprint_id = None):
        """"Gets the 3 sprint average velocity for a board as of a specific sprint

        Args:
            board_id: string - the id of a Jira board
            sprint_id: string - the id of a Jira sprint (defaults to None, in which case it assumes the most recently completely sprint)

        Returns:
            integer - The 3 sprint average velocity for the board_id as of the sprint_id provided
        """
        velocity_report = self.__makeRequest('GET',f"{self.__greenhopper_url}rapid/charts/velocity?rapidViewId={board_id}")

        if velocity_report == False:
            raise Exception(f"Unable to get velocity report for board {board_id}")

        total = 0
        sprints = 0
        found_sprint = True if sprint_id == None else False

        for sprint in sorted(velocity_report['velocityStatEntries'], reverse=True):
            if sprints >= 3:
                # We only care about the last three sprints
                break;

            if found_sprint == True or sprint_id == sprint:
                found_sprint = True
                total = total +  velocity_report['velocityStatEntries'][sprint]['completed']['value']
                sprints = sprints + 1

        return int(total/sprints) if sprints > 0 else total

    def generateGoogleFormURL(self, sprint_report_data):
        """Generates a URL that will pre-populate a specific AgileOps Google Form where teams submit their sprint metrics

        Args:
            sprint_report_data: dictionary - AgileOps Sprint Report Data

        Returns:
            string - A URL to a google form with relevant information pre-populate via query parameters
        """
        url = 'https://docs.google.com/forms/d/e/1FAIpQLSdF__V1ZMfl6H5q3xIQhSkeZMeCNkOHUdTBFdYA1HBavH31hA/viewform?'

        google_entry_translations = {
        "issue_metrics": {
            "items": {
                "bugs_completed": 'entry.448087930',
                "committed": 'entry.2095001800',
                "completed": 'entry.1399119358',
                "not_completed": 'entry.128659456',
                "planned_completed": 'entry.954885633',
                "removed": 'entry.1137054034',
                "stories_completed": 'entry.1980453543',
                "unplanned_bugs_completed": 'entry.1252702382',
                "unplanned_completed": 'entry.485777497',
                "unplanned_stories_completed": 'entry.370334542'
            },
            "points": {
                "committed": 'entry.1427603868',
                "completed": 'entry.1486076673',
                "feature_completed": 'entry.254612996',
                "not_completed": 'entry.611444996',
                "optimization_completed": 'entry.2092919144',
                "planned_completed": 'entry.493624591',
                "removed": 'entry.976792423',
                "unplanned_completed": 'entry.1333444050'
            }
        },
        #TODO: We're assuming that the project name IS the team name, which isn't always the case
        "project_key": "entry.1082637073",
        "sprint_number": "entry.1975251686"
        }

        try:
            for entry in ["project_key", "sprint_number"]:
                url += f"{google_entry_translations[entry]}={sprint_report_data[entry]}&"

            for metric_type in sprint_report_data['issue_metrics'].keys():
                if metric_type in ["meta", "issue_keys"]:
                    continue
                for item in sprint_report_data['issue_metrics'][metric_type].keys():
                    url += f"{google_entry_translations['issue_metrics'][metric_type][item]}={sprint_report_data['issue_metrics'][metric_type][item]}&"
        except (KeyError):
            raise Exception("Unable to generate Google Form URL, expected keys missing")

        return url

    def generateNextSprintNotionReplacementDictionary(self, sprint_report_data):
        """
        Generates a dictionary who's keys are special tags placed in notion docs like `[sprint-number]` and values are the relevant data.

        This function assumes that the data being passed in is for the 'next sprint' and acts accordingly

        Args:
            sprint_report_data: dictionary - AgileOps Sprint Report data

        Returns:
            dictionary - key / value pairs that will facilitate a search and replace in a notion document to populate it with relevant data
        """
        notion_dictionary = {}

        try:
            start_date = datetime.strptime(sprint_report_data['sprint_start'].split('T')[0], '%d/%b/%y %I:%M %p')
            end_date = datetime.strptime(sprint_report_data['sprint_end'].split('T')[0], '%d/%b/%y %I:%M %p')

            notion_dictionary['[next-sprint-number]'] = sprint_report_data['sprint_number']
            notion_dictionary['[next-sprint-start]'] = datetime.strftime(start_date, '%m/%d/%Y')
            notion_dictionary['[next-sprint-end]'] = datetime.strftime(end_date, '%m/%d/%Y')

            notion_dictionary['[next-sprint-goal]'] = "\n".join(sprint_report_data['sprint_goals'])

            notion_dictionary['[next-points-committed]'] = str(sprint_report_data['issue_metrics']['points']['committed'])
            notion_dictionary['[next-items-committed]'] = str(sprint_report_data['issue_metrics']['items']['committed'])

            notion_dictionary['[next-original-committed-link]'] =f"[{sprint_report_data['issue_metrics']['items']['committed']} Committed Issues]({self.generateJiraIssueLink(sprint_report_data['issue_metrics']['issue_keys']['committed'])})"

        except KeyError:
            raise Exception("Unable to generate a Notion Replacement Dictionary, keys not found")

        return notion_dictionary

    def generateNotionReplacementDictionary(self, sprint_report_data):
        """
        Generates a dictionary who's keys are special tags placed in notion docs like `[sprint-number]` and values are the relevant data.

        This function assumes that the data being passed in is for the 'current sprint' and acts accordingly

        Args:
            sprint_report_data: dictionary - AgileOps Sprint Report data

        Returns:
            dictionary - key / value pairs that will facilitate a search and replace in a notion document to populate it with relevant data
        """
        notion_dictionary = {}

        try:
            start_date = datetime.strptime(sprint_report_data['sprint_start'].split('T')[0], '%d/%b/%y %I:%M %p')
            end_date = datetime.strptime(sprint_report_data['sprint_end'].split('T')[0], '%d/%b/%y %I:%M %p')

            notion_dictionary['[team-name]'] = sprint_report_data['project_name']
            notion_dictionary['[sprint-number]'] = sprint_report_data['sprint_number']
            notion_dictionary['[sprint-start]'] = datetime.strftime(start_date, '%m/%d/%Y')
            notion_dictionary['[sprint-end]'] = datetime.strftime(end_date, '%m/%d/%Y')
            notion_dictionary['[sprint-goal]'] = "\n".join(sprint_report_data['sprint_goals'])
            notion_dictionary['[points-committed]'] = str(sprint_report_data['issue_metrics']['points']['committed'])
            notion_dictionary['[points-completed]'] = str(sprint_report_data['issue_metrics']['points']['completed'])

            notion_dictionary['[items-committed]'] = str(sprint_report_data['issue_metrics']['items']['committed'])
            notion_dictionary['[items-completed]'] = str(sprint_report_data['issue_metrics']['items']['completed'])
            notion_dictionary['[bugs-completed]'] = str(sprint_report_data['issue_metrics']['items']['bugs_completed'])

            notion_dictionary['[predictability]'] = str(sprint_report_data['issue_metrics']['meta']['predictability']) + "%"
            notion_dictionary['[predictability-commitments]'] = str(sprint_report_data['issue_metrics']['meta']['predictability_of_commitments']) + "%"
            notion_dictionary['[average-velocity]'] = str(sprint_report_data['average_velocity'])

            notion_dictionary['[original-committed-link]'] =f"[{sprint_report_data['issue_metrics']['items']['committed']} Committed Issues]({self.generateJiraIssueLink(sprint_report_data['issue_metrics']['issue_keys']['committed'])})"

            notion_dictionary['[completed-issues-link]'] = f"[{sprint_report_data['issue_metrics']['items']['completed']} Completed Issues]({self.generateJiraIssueLink(sprint_report_data['issue_metrics']['issue_keys']['completed'])})"

            notion_dictionary['[items-not-completed-link]'] = f"[{sprint_report_data['issue_metrics']['items']['not_completed']} Incomplete Issues]({self.generateJiraIssueLink(sprint_report_data['issue_metrics']['issue_keys']['incomplete'])})"

            notion_dictionary['[items-removed-link]'] = f"[{sprint_report_data['issue_metrics']['items']['removed']} Removed Issues]({self.generateJiraIssueLink(sprint_report_data['issue_metrics']['issue_keys']['removed'])})"

        except KeyError:
            raise Exception("Unable to generate a Notion Replacement Dictionary, keys not found")

        return notion_dictionary

    def generateJiraIssueLink(self, issues):
        """Generates a link to a collection of Jira issues

        Args:
            issues: list - Jira issue id's

        Returns:
            string - A Jira link that will display the passed in issues
        """
        link =  f"https://{self.__host}/issues/?jql=issueKey%20in%20("

        for issue in issues:
            link += f"{issue}%2C"

        link = re.sub(r'\%2C$', '', link) + ")"

        return link

    def getCommandsRegex(self):
        """Used by the bot to retrieve regex strings and commands that we support

        Returns:
            dictionary - regex strings and function references that are associated with them
        """
        return self.__regex

    def getCommandDescriptions(self):
        """Used by the bot to provide helpful information to the user about the commands we support

        Returns:
            dictionary - commands and their associated helpful descriptions
        """
        return self.__descriptions
