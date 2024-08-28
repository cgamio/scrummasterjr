import os, logging, re, datetime

from atlassian import Confluence

if __name__ == '__main__':

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO')
    )

    confluence = Confluence(
        url=f"https://{os.environ['JIRA_HOST']}",
        username=os.environ["JIRA_USER"],
        password=os.environ["JIRA_TOKEN"]
    )

    current_sprint_string = os.environ["CURRENT_SPRINT"]
    current_sprint_split = current_sprint_string.split('.', 1)
    next_sprint = f"{current_sprint_split[0]}.{int(current_sprint_split[1])+1}"

    # Assume that this is going to run on the Monday before the sprint ending on Wednesday
    now = datetime.datetime.now()-datetime.timedelta(days=12)
    start_date = now.strftime('%m/%d')
    end_date = (now+datetime.timedelta(days=2)).strftime('%m\%d')

    presenting_string = "A-K" if int(current_sprint_split[1])%2 else "J-Z"

    template_page_id = os.environ["TEMPLATE_PAGE_ID"]
    parent_page_id = os.environ["PARENT_PAGE_ID"]

    source = confluence.get_page_by_id(template_page_id, expand='body.storage')
    newbody = source['body']['storage']['value']

    newbody = re.sub(r'\[sprint {sprint number}\]', f'[sprint {current_sprint_string}]', newbody)
    newbody = re.sub(r'\[next-sprint {sprint number}\]', f'[next-sprint {next_sprint}]', newbody)

    dest = confluence.update_or_create(parent_page_id, f"[PENDING METRICS] End of Sprint {current_sprint_split[1]} Report - {start_date} to {end_date} - {presenting_string} Presenting", newbody)