import os

from notion.client import NotionClient
from notion.block import PageBlock, HeaderBlock, DividerBlock, TodoBlock
from datetime import datetime
import logging
import re
from collections import deque

class NotionPage:

    def __init__(self, url):
        self.__client = NotionClient(token_v2=os.environ.get('NOTION_TOKEN'))
        self.blocks = self.__client.get_block(url)
        self.queue = None

    def searchAndReplace(self, replacement_dictionary, stopping_block_patterns = [], dictionary_update_callback = None):
        self.queue = deque(self.blocks.children)

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
                self.queue.extendleft(block.children)
            except AttributeError:
                logging.info("Block has no more children, end of the line")

            try:
                for pattern in stopping_block_patterns:
                    if re.match(pattern, block.title):
                        replacement_dictionary = dictionary_update_callback(block.title)
                        block.remove()
                        if "[next-sprint-goal]" in replacement_dictionary:
                            checkNextSprintGoals = True
                        if "[sprint-goal]" in replacement_dictionary:
                            checkSprintGoals = True
                        continue


                if checkSprintGoals and "[sprint-goal]" in block.title:
                    parent = block.parent
                    logging.info(f"Parent: {parent}")
                    for goal in replacement_dictionary['[sprint-goal]'].split("\n"):
                        new_block = parent.children.add_new(TodoBlock, title=goal)
                        new_block.move_to(block, "before")
                    block.remove()
                    continue

                if checkNextSprintGoals and "[next-sprint-goal]" in block.title:
                    parent = block.parent
                    logging.info(f"Parent: {parent}")
                    for goal in replacement_dictionary['[next-sprint-goal]'].split("\n"):
                        new_block = parent.children.add_new(TodoBlock, title=goal)
                        new_block.move_to(block, "before")
                    block.remove()
                    continue

                new_title = block.title

                for search, replace in replacement_dictionary.items():
                    new_title = new_title.replace(search, replace)

                if block.title != new_title:
                    logging.info(f"{block.title} -> {new_title}")
                    block.title = new_title
            except AttributeError:
                logging.info("Block has no title, moving on")
