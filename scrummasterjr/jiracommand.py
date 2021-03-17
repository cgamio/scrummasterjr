from scrummasterjr.basecommand import BaseCommand
from scrummasterjr.jira import Jira
from scrummasterjr.error import ScrumMasterJrError
import logging
import re

class JiraCommand (BaseCommand):

    def __init__ (self, jira, prefix = None):
        self.prefix = ""
        if prefix:
            self.prefix = f"{prefix} "
        self.jira = jira
        regex = {
            f'test {self.prefix}jira': self.testConnection,
            rf'{self.prefix}sprint report (?P<sprint_id>[0-9]+)\s*((?P<next_sprint_id>[0-9]+)\s*<?(?P<notion_url>https://www.notion.so/[^\s>]+))?': self.getSprintReport
        }
        descriptions = {
            f'test {self.prefix}jira': 'tests my connection to jira',
            f'{self.prefix}sprint report [sprint-id] [next-sprint-id] [notion-url]': 'get a quick sprint report for a given sprint, the next sprint, and then update the given notion page'
        }
        super().__init__(regex, descriptions)

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

    def showSprintReportModal(self, ack, body, client, command, respond):
        ack()

        results = self.jira.getBoardsInProject(command['text'].strip())

        if not results:
            respond(
                {
                    "text": "Please provide a valid Jira Project Key with this command",
                    "response_type": "ephemeral"
                }
            )
            return

        board_options = []

        for board in results["values"]:
            if board['type'] == "scrum":
                board_options.append(
                    {
                        "text": {
                            "type": "plain_text",
                            "text": board["name"]
                        },
                        "value": str(board["id"])
                    }
                )

        if not board_options:
            respond(
                {
                    "text": "I'm only able to generate sprint reports for projects that use Scrum boards. Please reach out in <#C6GJGERFC> if you need help getting one set up.",
                    "response_type": "ephemeral"
                }
            )
            return

        modal_view = {
    	"title": {
    		"type": "plain_text",
    		"text": "Run Sprint Report"
    	},
    	"type": "modal",
    	"close": {
    		"type": "plain_text",
    		"text": "Cancel"
    	},
        "submit": {
            "type": "plain_text",
            "text": "Run"
        },
    	"blocks": [
    		{
                "block_id": "board_section",
    			"type": "input",
    			"label": {
    				"type": "plain_text",
    				"text": "Which board did you mean?"
    			},
    			"element": {
    				"type": "static_select",
    				"placeholder": {
    					"type": "plain_text",
    					"text": "Select a board"
    				},
    				"options": board_options,
    				"action_id": "board_select_action"
    			},
                "dispatch_action": True
    		}]
        }

        # Call views_open with the built-in client
        client.views_open(
             # Pass a valid trigger_id within 3 seconds of receiving it
            trigger_id=body["trigger_id"],
            # View payload
            view=modal_view
        )

    def showSprints(self, ack, body, client, context):

        results = self.jira.getSprintsInBoard(body['actions'][0]['selected_option']['value'])
        sprints = []

        for sprint in results['values']:
            sprints.append(
                {
                    "text": {
                        "type": "plain_text",
                        "text": sprint['name'] if sprint['state'] != 'active' else f"{sprint['name']} *Active Sprint*"
                    },
                    "value": f"{sprint['id']}"
                }
            )

        if not sprints:
            error_block = {
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": ":warning: This board has no sprints, please select another :warning:"
    			}
    		}

            body["view"]["blocks"] = [body["view"]["blocks"][0], error_block]
            client.views_update(
                hash=body["view"]["hash"],
                view_id=body["view"]["id"],
                view = {
                    "type": body["view"]["type"],
                    "title": body["view"]["title"],
                    "callback_id": "report_input_view",
                	"submit": {
                		"type": "plain_text",
                		"text": "Run"
                	},
                    "blocks": body['view']['blocks']
                }
            )
            return

        sprint_blocks = [{
            "type": "input",
            "block_id": "completed_sprint_section",
            "label": {
                "type": "plain_text",
                "text": "Completed sprint"
            },
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a sprint"
                },
                "options": sprints
            }
        },
        {
            "type": "input",
            "block_id": "upcoming_sprint_section",
            "label": {
                "type": "plain_text",
                "text": "Upcoming sprint"
            },
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a sprint"
                },
                "options": sprints,
            }
        }]

        notion_block = {
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "notion_url_input_action",
				"placeholder": {
					"type": "plain_text",
					"text": "Paste a Notion URL to update here"
				}
			},
			"label": {
				"type": "plain_text",
				"text": "Notion URL"
			}
		}


        new_blocks = [body["view"]["blocks"][0]]
        new_blocks.extend(sprint_blocks)

        client.views_update(
            hash=body["view"]["hash"],
            view_id=body["view"]["id"],
            view = {
                "type": body["view"]["type"],
                "title": body["view"]["title"],
                "callback_id": "report_input_view",
            	"submit": {
            		"type": "plain_text",
            		"text": "Run"
            	},
                "blocks": new_blocks
            }
        )

    def runSprintReport(self, ack, body, client, context):

        board_state_values = body['view']['state']['values']

        board_id = board_state_values['board_section']['board_select_action']['selected_option']['value']
        completed_sprint_id = None
        upcoming_sprint_id = None

        errors = {}
        new_view = {}

        try:

            try:
                completed_sprint_id = list(board_state_values['completed_sprint_section'].values())[0]['selected_option']['value']
            except TypeError:
                errors["completed_sprint_section"] = 'Please select a sprint'

            try:
                upcoming_sprint_id = list(board_state_values['upcoming_sprint_section'].values())[0]['selected_option']['value']
            except TypeError:
                errors["upcoming_sprint_section"] = 'Please select a sprint'
        except KeyError:
            new_view = {
                "type": body["view"]["type"],
                "title": body["view"]["title"],
                "callback_id": "error_view",
                "blocks": [
            		{
            			"type": "image",
            			"image_url": "https://media2.giphy.com/media/Px7FQJqhWTGaA/giphy.gif?cid=ecf05e477ls5y92dm0xp0yqwfblydgcaek7p09t27zdv0tk3&rid=giphy.gif",
            			"alt_text": "broken computer"
            		},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"That board has no sprints... Please press cancel and choose another"
                        }
                    }
                ]
            }

        if errors:
            ack(response_action="errors", errors=errors)
            return


        if not new_view:
            new_view = {
                "type": body["view"]["type"],
                "title": body["view"]["title"],
                "callback_id": "report_results_view",
                "external_id": "sprint_results_view_id",
                "blocks": [
                    {
            			"type": "image",
                        "title": {
            				"type": "plain_text",
            				"text": "Processing... Please wait"
            			},
            			"image_url": "https://media2.giphy.com/media/26gR0YFZxWbnUPtMA/giphy.gif?cid=ecf05e47e10dxbfzuw3ibaewju07n66c9j38iqbb0d95oroy&rid=giphy.gif",
            			"alt_text": "thinking"
            		}
                ]
            }

        ack(
            {
                "response_action": "push",
                "view": new_view

            }
        )

        completed_sprint_report_data = self.jira.generateAllSprintReportData(completed_sprint_id)

        new_view['blocks'] = [{
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": completed_sprint_report_data['project_name']
            }
        }]

        sprint_goals_string = '\n'.join(completed_sprint_report_data['sprint_goals'])

        new_view['blocks'].append(
            {
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": f"*Sprint {completed_sprint_report_data['sprint_number']}*\n{sprint_goals_string}"
    			}
    		}
        )

        new_view["submit"] = {
            "type": "plain_text",
            "text": "Submit Metrics"
        }

        new_view["close"] = {
            "type": "plain_text",
            "text": "Done"
        }

        client.views_update(
            external_id=new_view["external_id"],
            view = new_view
        )
        #
        # blocks = [
    	# 	,
    	# 	,
    	# 	{
    	# 		"type": "section",
    	# 		"text": {
    	# 			"type": "mrkdwn",
    	# 			"text": "*COLI - Sprint 2*\nDo some other things"
    	# 		}
    	# 	},
    	# 	{
    	# 		"type": "header",
    	# 		"text": {
    	# 			"type": "plain_text",
    	# 			"text": "Metrics",
    	# 			"emoji": true
    	# 		}
    	# 	},
    	# 	{
    	# 		"type": "section",
    	# 		"fields": [
    	# 			{
    	# 				"type": "plain_text",
    	# 				"text": "Velocity",
    	# 				"emoji": true
    	# 			},
    	# 			{
    	# 				"type": "plain_text",
    	# 				"text": "27 pts",
    	# 				"emoji": true
    	# 			},
    	# 			{
    	# 				"type": "plain_text",
    	# 				"text": "Predicability of Commitments",
    	# 				"emoji": true
    	# 			},
    	# 			{
    	# 				"type": "plain_text",
    	# 				"text": "95%",
    	# 				"emoji": true
    	# 			}
    	# 		]
    	# 	}
        # ]
