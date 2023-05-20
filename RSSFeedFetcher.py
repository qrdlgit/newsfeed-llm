import feedparser
import hashlib
from FeedCLI import *
from datetime import datetime


class RSSFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.feed_url = config['feed_url']
        self.entry_properties = config.get('entry_properties', ['title', 'description'])
        self.text_properties = config.get('text_properties', ['title', 'description'])
        self.seen_items = {}
        self.last_seen_date = datetime.now()

    def get_new_feed_items(self):
        # Parse the RSS feed
        feed = feedparser.parse(self.feed_url)

        # Filter items that are newer than the last seen date and not duplicates
        new_feed_items = []
        for entry in feed.entries:
            entry_date = datetime(*entry.published_parsed[:6])  # Convert time struct to datetime
            print(entry_date, self.last_seen_date)
            if entry_date > self.last_seen_date:
                # Create a hash from a list of entry properties
                entry_hash_text = ' '.join(str(entry.get(prop)) for prop in self.entry_properties)
                entry_hash = hashlib.sha256(entry_hash_text.encode()).hexdigest()

                # If this is a new item, add it to the list
                if entry_hash not in self.seen_items:
                    self.seen_items[entry_hash] = entry_hash_text
                    entry_text = ' '.join(str(entry.get(prop)) for prop in self.text_properties)
                    new_feed_items.append(entry_text)

        return new_feed_items


