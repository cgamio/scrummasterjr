from scrummasterjr.basecommand import BaseCommand
from scrummasterjr.jira import Jira
from scrummasterjr.error import ScrumMasterJrError
import logging
import re

class JiraCommand (BaseCommand):

    def __init__ (self, jira, prefix = ""):
        self.prefix = prefix
        self.jira = jira
        regex = {
            f'test {self.prefix}jira': self.testConnection,
            rf'{self.prefix}sprint report (?P<sprint_id>[0-9]+)\s*((?P<next_sprint_id>[0-9]+)\s*<?(?P<notion_url>https://www.notion.so/[^\s>]+))?': self.getSprintReport
        }
        description = {
            f'test {self.prefix}jira': 'tests my connection to jira',
            f'{self.prefix}sprint report [sprint-id] [next-sprint-id] [notion-url]': 'get a quick sprint report for a given sprint, the next sprint, and then update the given notion page'
        }
        super().__init__(regex, description)

    def testConnection(self, slack_event):
        response = self.jira.testConnection()
        text = "My connection to Jira is up and running!"
        if not response:
            logging.error(f"Error with Jira connection: {response}")
            text = "Looks like there's an issue with my connection. I've logged an error"

        return text

    def getSprintReport(self, slack_event):

        error = None

        regex_result = re.search(r'sprint report (?P<sprint_id>[0-9]+)\s*((?P<next_sprint_id>[0-9]+)\s*<?(?P<notion_url>https://www.notion.so/[^\s>]+))?', slack_event['text']).groupdict()

        report_data = self.jira.generateAllSprintReportData(regex_result['sprint_id'])

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
                "text": f"<{self.jira.generateGoogleFormURL(report_data)}|Google Form URL>"
            }
            })

        if regex_result['notion_url'] and regex_result['next_sprint_id']:
            next_report_data = self.jira.generateAllSprintReportData(regex_result['next_sprint_id'])
            if 'text' in next_report_data: return next_report_data

            result = self.jira.updateNotionPage(regex_result['notion_url'], report_data, next_report_data)

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

        if error:
            raise ScrumMasterJrError({"blocks": blocks}, error)

        return {"blocks": blocks}
