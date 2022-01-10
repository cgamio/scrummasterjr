import os

from atlassian import Confluence

from datetime import datetime
import logging
import re
from collections import deque

from bs4 import BeautifulSoup

class ConfluencePage:

    def __init__(self, page_url):
        self.__client = Confluence(
            url=f"https://{os.environ['JIRA_HOST']}",
            username=os.environ["JIRA_USER"],
            password=os.environ["JIRA_TOKEN"]
        )
        page_id = re.search("(\d*)\/[^\/]*$", page_url).groups()[0]
        logging.info(f"Page URL: {page_url}\nPage ID: {page_id}")
        self.page = self.__client.get_page_by_id(page_id, expand='body.storage')
        self.contents = self.page['body']['storage']['value']
        self.queue = None

    def searchAndReplace(self, replacement_dictionary, stopping_block_patterns = [], dictionary_update_callback = None):
        soup = BeautifulSoup(self.contents, 'html.parser')
        self.queue = deque(soup.contents)

        checkSprintGoals = False
        if "[sprint-goal]" in replacement_dictionary:
            checkSprintGoals = True

        checkNextSprintGoals = False
        if "[next-sprint-goal]" in replacement_dictionary:
            checkNextSprintGoals = True

        while self.queue:
            block = self.queue.popleft()
            logging.info(f"Processing Block: {block}")

            try:
                self.queue.extendleft(block.contents)
                continue
            except AttributeError:
                logging.info("Block has no more children, end of the line")

            try:
                for pattern in stopping_block_patterns:
                    if re.match(pattern, block.string):
                        replacement_dictionary = dictionary_update_callback(block.string)
                        block.replace_with()
                        if "[next-sprint-goal]" in replacement_dictionary:
                            checkNextSprintGoals = True
                        if "[sprint-goal]" in replacement_dictionary:
                            checkSprintGoals = True
                        continue


                if checkSprintGoals and "[sprint-goal]" in block.string:
                    parent = block.parent
                    logging.info(f"Parent: {parent}")
                    list = soup.new_tag('ul')
                    for goal in replacement_dictionary['[sprint-goal]'].split("\n"):
                        list_item = soup.new_tag('li')
                        p_item = soup.new_tag('p')
                        p_item.string = goal
                        list_item.append(p_item)
                        list.append(list_item)
                    parent.replace_with(list)
                    continue

                if checkNextSprintGoals and "[next-sprint-goal]" in block.title:
                    parent = block.parent
                    logging.info(f"Parent: {parent}")
                    list = soup.new_tag('ul')
                    for goal in replacement_dictionary['[next-sprint-goal]'].split("\n"):
                        list_item = soup.new_tag('li')
                        p_item = soup.new_tag('p')
                        p_item.string = goal
                        list_item.append(p_item)
                        list.append(list_item)
                    parent.replace_with(list)
                    continue

                new_title = block.string

                for search, replace in replacement_dictionary.items():
                    new_title = new_title.replace(search, replace)

                if block.string != new_title:
                    logging.info(f"{block.string} -> {new_title}")
                    block.string.replace_with(new_title)
            except AttributeError:
                logging.info("Block has no title, moving on")

        logging.info(f"------------------------\nSoup:\n{soup}\n------------------------")

        if self.contents != soup:
            self.__client.update_page(self.page_id, self.page['title'], body=str(soup), representation="storage", always_update=True)
