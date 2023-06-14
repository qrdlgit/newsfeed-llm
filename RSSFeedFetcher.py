import feedparser
import hashlib
from FeedCLI import *
from datetime import datetime, timedelta
import logging

class RSSFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.feed_url = config['feed_url']
        self.entry_properties = config.get('entry_properties', ['title', 'description'])
        self.text_properties = config.get('text_properties', ['title', 'description'])
        self.feed_weight = config.get('feed_weight', 1)
        self.feed_type = config.get('feed_type', "news")
        self.top_config = config.get('top', {})
        self.back_days = self.top_config.get('back_days',1)

        self.seen_items = {}
        self.last_seen_date = datetime.now() - timedelta(days=self.back_days)

    def get_date(self, entry):
        if 'published_parsed' in entry:
            return datetime(*entry['published_parsed'][:6])
        elif 'updated_parsed' in entry:
            return datetime(*entry['updated_parsed'][:6])
        else:
            return None
        
    def get_new_feed_items(self):
        # Parse the RSS feed
        try:
            feed = feedparser.parse(self.feed_url)
            feed_date = self.get_date(feed)
            # Filter items that are newer than the last seen date and not duplicates
            new_feed_items = []
            for entry in feed.entries:
                entry_date = self.get_date(entry)
                if entry_date == None:
                    entry_date = feed_date
                #print(entry_date, self.last_seen_date)
                if entry_date > self.last_seen_date:
                    # Create a hash from a list of entry properties
                    entry_hash_text = ' '.join(str(entry.get(prop)) for prop in self.entry_properties)
                    entry_hash = hashlib.sha256(entry_hash_text.encode()).hexdigest()
                else:
                    continue
                # If this is a new item, add it to the list
                if entry_hash not in self.seen_items:
                    self.seen_items[entry_hash] = entry_hash_text
                    entry_text = ' '.join(str(entry.get(prop)) for prop in self.text_properties)
                    item = {'feed_type':self.feed_type, 'feed_weight':self.feed_weight, 
                            'text':entry_text, 'title':entry['title'], 'link':entry['link']}
                    new_feed_items.append(item)
        except Exception as e:
            logging.error(f"issue with {self.feed_url} {e}")
            return []

        return new_feed_items


