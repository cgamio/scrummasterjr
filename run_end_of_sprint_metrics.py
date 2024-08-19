import os
from scrummasterjr.jira import Jira
import logging, re

from atlassian import Confluence

if __name__ == '__main__':

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO')
    )

    jira_host = os.environ["JIRA_HOST"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]

    jira = Jira(jira_host, jira_user, jira_token)
    confluence = Confluence(
        url=f"https://{os.environ['JIRA_HOST']}",
        username=os.environ["JIRA_USER"],
        password=os.environ["JIRA_TOKEN"]
    )

    parent_page_id = os.environ["PARENT_PAGE_ID"]

    children = confluence.get_child_pages(parent_page_id)

    for child in children:
        if child['title'].startswith('[PENDING METRICS]'):
            print(f"Updating page https://{os.environ['JIRA_HOST']}/wiki/{child['_links']['webui']}")
            jira.updateNotionSummaryPage(f"https://{os.environ['JIRA_HOST']}/wiki/{child['_links']['webui']}")
            confluence.update_page(child['id'], title=child['title'].replace("[PENDING METRICS]", ""))
            exit()

    exit(1)