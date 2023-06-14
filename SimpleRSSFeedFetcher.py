import feedparser
import hashlib
from FeedCLI import *
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup

def extract_text(html_string):
    soup = BeautifulSoup(html_string, "html.parser")
    return soup.get_text()


class SimpleRSSFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.feed_url = config['feed_url']
        self.text_properties = config.get('text_properties', ['title', 'description'])
        self.feed_weight = config.get('feed_weight', 1)
        self.feed_type = config.get('feed_type', "news")


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
                entry_text = ' '.join(str(entry.get(prop)) for prop in self.text_properties)
                entry_text = extract_text(entry_text)
                item = {'feed':self.feed_url, 'feed_type':self.feed_type, 'feed_weight':self.feed_weight, 
                        'text':entry_text, 'title':entry['title'], 'link':entry['link'], 'date':entry_date}
                new_feed_items.append(item)
        except Exception as e:
            logging.error(f"issue with {self.feed_url}  {e}")
            return []

        return new_feed_items


