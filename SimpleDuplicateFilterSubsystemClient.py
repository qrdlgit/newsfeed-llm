from FilterSubsystemClient import FilterSubsystemClient
import oai
import utils
import numpy as np
import hashlib
embeds = []

class SimpleDuplicateFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)
        self.oai = config['oai']
        self.db = config['db']
        self.dupe_table = {}
        self.init_dupe_table()

    # self.db has interface get_items which gets all items
    # calls self.get_items and generates hashes for all item['title']
    def init_dupe_table(self):
        items = self.db.get_items()  # Assuming this returns a list of dicts
        for item in items:
            self.dupe_table[item['title']] = 'T'

    # hashes item['title'] and checks for dupe in dupe_table
    # if found, returns 0
    # else adds to dupe_table and returns 999
    def get_score(self, item):
        if item['title'] in self.dupe_table:
            return 999
        else:
            self.dupe_table[item['title']] = 'T'
            return 0

