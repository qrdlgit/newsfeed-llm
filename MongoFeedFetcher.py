from pymongo import MongoClient
import hashlib
from FeedCLI import *
import datetime
from datetime import timedelta
import logging
import bs4

class MongoFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient(config.get("mongo_uri", "mongodb://192.168.1.86"))
        self.db = self.client[config.get("db_name","wiki_jobs" )]
        self.collection = self.db[config.get("collection_name", "all_txts")]
        self.feed_weight = config.get('feed_weight', 1)
        self.seen_items = {}
        self.feed_url = config.get('feed_url', '')
        self.td = config.get('td', 10)
        self.usernames = config.get('usernames', [])

    def get_new_feed_items(self):
        ts = round((datetime.datetime.now() - datetime.timedelta(minutes=self.td)).timestamp())
        all_txts = self.collection
        last60 = list(all_txts.find({'ts':{'$gt':ts}}))
        new_feed_items = []
        for item in last60:
            entry_text = item['txt']
            feed_type = item['src']+"_"+item['u']
            ts = item['ts']
            entry_hash = hashlib.sha256(entry_text.encode()).hexdigest()
            if entry_hash not in self.seen_items:
                self.seen_items[entry_hash] = True
            else:
                continue
            if self.usernames != [] and item['u'] and item['u'].lower() not in self.usernames:
                continue
            item = {'hash':entry_hash, 'username':item['u'], 'feed_type':feed_type, 'feed_weight':self.feed_weight, 
                'text':entry_text, 'title':item['u'], 'link':item['u'], 'ts':ts}
            new_feed_items.append(item)
        logging.info(f"Mongo new feed items: {len(new_feed_items)}")
        return new_feed_items
        


            
