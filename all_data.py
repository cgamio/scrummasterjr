import os
from scrummasterjr.jira import Jira
from scrummasterjr.error import ScrumMasterJrError
import logging

if __name__ == '__main__':

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO')
    )

    jira_host = os.environ["JIRA_HOST"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    jira = Jira(jira_host, jira_user, jira_token)

    teams = {
        "Dirigible": 37,
        "Emu": 30,
        "Fire Ferrets": 42,
        "HODL": 46,
        "Juggernaut": 45,
        "Limitless": 52,
        "Mystery Inc": 66,
        "DevOps": 61,
        "Paradise": 48,
        "Urban Chickens": 40,
        "Snacks": 27
    }

    f = open('all_sprint_data.txt', 'a')

    for team in teams.keys():
        print(f"Team = {team}")
        sprints = jira.getSprintsInBoard(teams[team])
        for sprint in sprints:
            print(f"    Sprint = {sprint['name']}")
            try:
                data = jira.generateAllSprintReportData(sprint['id'])
                f.write(f"{team},{sprint['name']},{data['sprint_start']},{data['sprint_end']},{data['issue_metrics']['points']['committed']},{data['issue_metrics']['points']['completed']},{data['issue_metrics']['points']['planned_completed']},{data['issue_metrics']['points']['unplanned_completed']},{data['issue_metrics']['points']['feature_completed']},{data['issue_metrics']['points']['optimization_completed']},{data['issue_metrics']['points']['not_completed']},{data['issue_metrics']['points']['removed']},{data['issue_metrics']['items']['committed']},{data['issue_metrics']['items']['completed']},{data['issue_metrics']['items']['planned_completed']},{data['issue_metrics']['items']['unplanned_completed']},{data['issue_metrics']['items']['stories_completed']},{data['issue_metrics']['items']['unplanned_stories_completed']},{data['issue_metrics']['items']['bugs_completed']},{data['issue_metrics']['items']['unplanned_bugs_completed']},{data['issue_metrics']['items']['not_completed']},{data['issue_metrics']['items']['removed']},{data['issue_metrics']['items']['added']},{data['issue_metrics']['meta']['predictability']},{data['issue_metrics']['meta']['predictability_of_commitments']},{data['average_velocity']},{data['average_predictability']},{data['average_predictability_of_commitments']}\n")
            except:
                continue


    f.close()
