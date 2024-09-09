import os, sys
from scrummasterjr.jira import Jira
from scrummasterjr.error import ScrumMasterJrError
import logging, re

if __name__ == '__main__':

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO')
    )

    jira_host = os.environ["JIRA_HOST"]
    jira_user = os.environ["JIRA_USER"]
    jira_token = os.environ["JIRA_TOKEN"]
    jira = Jira(jira_host, jira_user, jira_token)

    teams = {
        "Emu": (30,'E'),
        "Fire Ferrets": (42,'F'),
        "HODL": (46,'H'),
        "Jedi": (157, 'J'),
        "DevOps": (61,'O'),
        "Paradise": (48,'P'),
        "Snacks": (27,'S'),
	"Unicorn": (89, 'U'),
	"Atlantis": (92, 'A'),
	"Yeet": (119, 'Y'),
	"Zeppelin": (37, 'Z'),
	"Merlin": (165, 'M'),
	"Keto-memes": (162, 'K')
    }

    f = open('all_sprint_data.txt', 'a')

    for team in teams.keys():
        (board_id, team_letter) = teams[team]
        print(f"Team = {team}")
        sprints = jira.getSprintsInBoard(board_id)

        if len(sys.argv) > 1:
            sprint = jira.getMatchingSprintInBoard(board_id, f"{sys.argv[1]}{team_letter}")
            try:
                data = jira.generateAllSprintReportData(sprint['id'])
                f.write(f"{team},{sprint['name']},{data['sprint_start']},{data['sprint_end']},{data['issue_metrics']['points']['committed']},{data['issue_metrics']['points']['completed']},{data['issue_metrics']['points']['planned_completed']},{data['issue_metrics']['points']['unplanned_completed']},{data['issue_metrics']['points']['feature_completed']},{data['issue_metrics']['points']['optimization_completed']},{data['issue_metrics']['points']['not_completed']},{data['issue_metrics']['points']['removed']},{data['issue_metrics']['items']['committed']},{data['issue_metrics']['items']['completed']},{data['issue_metrics']['items']['planned_completed']},{data['issue_metrics']['items']['unplanned_completed']},{data['issue_metrics']['items']['stories_completed']},{data['issue_metrics']['items']['unplanned_stories_completed']},{data['issue_metrics']['items']['bugs_completed']},{data['issue_metrics']['items']['unplanned_bugs_completed']},{data['issue_metrics']['items']['not_completed']},{data['issue_metrics']['items']['removed']},{data['issue_metrics']['items']['added']},{data['issue_metrics']['meta']['predictability']},{data['issue_metrics']['meta']['predictability_of_commitments']},{data['average_velocity']},{data['average_predictability']},{data['average_predictability_of_commitments']}\n")
            except:
                continue

        else :
            for sprint in sprints:
                print(f"    Sprint = {sprint['name']}")
                if(re.search(team_letter, sprint['name'])):
                    try:
                        data = jira.generateAllSprintReportData(sprint['id'])
                        f.write(f"{team},{sprint['name']},{data['sprint_start']},{data['sprint_end']},{data['issue_metrics']['points']['committed']},{data['issue_metrics']['points']['completed']},{data['issue_metrics']['points']['planned_completed']},{data['issue_metrics']['points']['unplanned_completed']},{data['issue_metrics']['points']['feature_completed']},{data['issue_metrics']['points']['optimization_completed']},{data['issue_metrics']['points']['not_completed']},{data['issue_metrics']['points']['removed']},{data['issue_metrics']['items']['committed']},{data['issue_metrics']['items']['completed']},{data['issue_metrics']['items']['planned_completed']},{data['issue_metrics']['items']['unplanned_completed']},{data['issue_metrics']['items']['stories_completed']},{data['issue_metrics']['items']['unplanned_stories_completed']},{data['issue_metrics']['items']['bugs_completed']},{data['issue_metrics']['items']['unplanned_bugs_completed']},{data['issue_metrics']['items']['not_completed']},{data['issue_metrics']['items']['removed']},{data['issue_metrics']['items']['added']},{data['issue_metrics']['meta']['predictability']},{data['issue_metrics']['meta']['predictability_of_commitments']},{data['average_velocity']},{data['average_predictability']},{data['average_predictability_of_commitments']}\n")
                    except:
                        continue


    f.close()
