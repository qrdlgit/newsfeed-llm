from pymongo import MongoClient
import hashlib
from FeedCLI import *
import datetime
from datetime import timedelta
import logging
import bs4
import requests

class ManifoldFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.feed_weight = config.get('feed_weight', 1)
        self.seen_items = {}
        self.feed_url = config['feed_url']

    def extract_and_join_text(self, json_obj):
        text_elements = []

        def extract(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'text':
                        text_elements.append(value)
                    else:
                        extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item)

        extract(json_obj)
        return ' '.join(text_elements)

    def get_new_feed_items(self):
        new_feed_items = []
        r = requests.get(f"https://manifold.markets/api/v0/comments?contractSlug={self.feed_url}").json()
        for i in r:
            entry_text = self.extract_and_join_text(i)
            feed_type = 'manifold_'+i['userName']
            ts = i['createdTime']/1000
            entry_hash = hashlib.sha256(entry_text.encode()).hexdigest()
            if entry_hash not in self.seen_items:
                self.seen_items[entry_hash] = True
            else:
                continue
            item = {'hash':entry_hash, 'username':'MF_'+i['userName'], 'feed_type':feed_type, 'feed_weight':self.feed_weight, 
                    'text':entry_text, 'title':i['userName'], 'link':i['userName'], 'ts':ts}
            new_feed_items.append(item)
        return new_feed_items
        


            
