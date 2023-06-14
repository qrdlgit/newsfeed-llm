import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from FilterSubsystemClient import FilterSubsystemClient
import importlib

# Use Python's built-in logging module for logging
logging.basicConfig(filename='feed_processor.log', level=logging.DEBUG)

class FeedManager:
    def __init__(self):
        self.feed_fetchers = []

    def add_feed(self, config):
        # Create a FeedFetcher based on the feed type and configuration
        feed_fetcher = FeedFetcher.getFeedFetcher(config)
        logging.info(f"add_feed {feed_fetcher}")
        self.feed_fetchers.append(feed_fetcher)

    def get_feeds(self):
        return self.feed_fetchers

class FeedItem:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text

class FeedFetcher(ABC):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def getFeedFetcher(config):
        try:
            src = config.get('src', 'SimpleRSSFeedFetcher')
            module = importlib.import_module(src)
            class_ = getattr(module, src)
            logging.info(f"getFeedFetcher class {class_}")
            return class_(config)
        except Exception as e:
            logging.error(f'Failed to load FeedFetcher from config {config}: {e}')
            return None

    @abstractmethod
    def get_new_feed_items(self):
        pass

class SummarySubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def getSubsystemClient(config):
        return FilterSubsystemClient.getSubsystemClient(config)

    @abstractmethod
    def get_summary(self, item):
        pass

class DataStorageSubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def getSubsystemClient(config):
        return FilterSubsystemClient.getSubsystemClient(config)

    @abstractmethod
    def store_item(self, item):
        pass

    @abstractmethod
    def handle_error(self):
        pass



class FeedCLI:
    def __init__(self):
        self.feed_manager = FeedManager()
        self.subsystem_clients = {}

    def start_system(self):
        # Initialize logging
        logging.basicConfig(filename='feed_processing.log', level=logging.INFO)

        # Load configuration from settings.json
        with open("settings.json") as file:
            config = json.load(file)

        db = DataStorageSubsystemClient.getSubsystemClient(config['db_subsystem'])
        self.subsystem_clients['DataStorage'] = db
        
        # Use FeedManager to add feeds based on configuration
        feed_count = config.get('feed_count',-1)
        count = 0
        for feed_config in config['feeds']:
            feed_config['top'] = config
            feed_config['db'] = db
            self.feed_manager.add_feed(feed_config)
            count = count + 1
            if count > feed_count:
                break

        # Create SubsystemClient for each subsystem and store it
        for subsystem_config in config['subsystems']:
            subsystem_config['db'] = db
            subsystem_config['oai'] = config['oai']
            subsys = FilterSubsystemClient.getSubsystemClient(subsystem_config)
            name = subsystem_config['name']
            logging.info(f"adding subystem {name} = {str(subsys)}")
            self.subsystem_clients[name] = subsys

        logging.info("System started. Processing feeds at intervals of {} seconds.".format(config['processing_interval']))

        # Start continuous feed processing
        while True:
            logging.info("Getting feeds")
            for feed_fetcher in self.feed_manager.get_feeds():
                
                # Create a new thread for processing each feed
                thread = threading.Thread(target=self.process_feed, args=(feed_fetcher, config,))
                thread.start()

            # Delay before the next loop iteration
            time.sleep(config['processing_interval'])

    def process_feed(self, feed_fetcher, config):
        # Get new feed items
        items = feed_fetcher.get_new_feed_items()

        for item in items:
            with open('titles.txt','a') as f:
                f.write(item['title']+"\n")
            if self.subsystem_clients['Local'].get_score(item) > config['local_threshold']:
                continue

            # Check duplication
            if self.subsystem_clients['Duplicate'].get_score(item) > config['duplicate_threshold']:
                continue

            # Process other subsystems
            # item['Summary'] = self.subsystem_clients['Summary'].get_summary(item)
            item['Relevance'] = self.subsystem_clients['Relevance'].get_score(item)
            item['Quality'] = self.subsystem_clients['Quality'].get_score(item)
            item['Credibility'] = self.subsystem_clients['Credibility'].get_score(item)
            item['Freshness'] = self.subsystem_clients['Freshness'].get_score(item)

            # Store the processed feed item
            self.subsystem_clients['DataStorage'].store_item(item)


if __name__ == "__main__":
    FeedCLI().start_system()
