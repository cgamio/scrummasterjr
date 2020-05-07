import os

from notion.client import NotionClient
from notion.block import PageBlock, HeaderBlock, DividerBlock, TodoBlock
from datetime import datetime
import logging

class NotionPage:

    def __init__(self, url):
        self.__client = NotionClient(token_v2=os.environ.get('NOTION_TOKEN'))
        self.blocks = self.__client.get_block(url)

    def searchAndReplace(self, replacement_dictionary):
        """
        This function assumes that the document contains instances of the keys in the replacement dictionary. It will traverse the document structure and replace any instances of those keys, with the values in the dictionary.

        Args:
            replacement_dictionary - a dictionary who's keys we want to replace with their values in this Notion page.

                Special cases:
                - `[sprint-goal]` and `[next-sprint-goal]`: These assume that the value is an array of goals, and will replace the key with a series of Todo blocks for each goal in the array

        Returns:
            Nothing
        """
        queue = []

        queue.extend(self.blocks.children)

        checkSprintGoals = False
        if "[sprint-goal]" in replacement_dictionary:
            checkSprintGoals = True

        checkNextSprintGoals = False
        if "[next-sprint-goal]" in replacement_dictionary:
            checkNextSprintGoals = True

        while queue:
            block = queue.pop()
            logging.info(f"Processing Block: {block}")

            try:
                queue.extend(block.children)
            except AttributeError:
                logging.info("Block has no more children, end of the line")

            try:
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
