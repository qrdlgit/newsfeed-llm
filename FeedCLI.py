import json
import logging
import threading
import time
from abc import ABC, abstractmethod

# Use Python's built-in logging module for logging
logging.basicConfig(filename='feed_processor.log', level=logging.DEBUG)

class FeedManager:
    def __init__(self):
        self.feed_fetchers = []

    def add_feed(self, config):
        # Create a FeedFetcher based on the feed type and configuration
        feed_fetcher = FeedFetcher(config)
        self.feed_fetchers.append(feed_fetcher)

    def get_feeds(self):
        return self.feed_fetchers

class FeedItem:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text

class FeedFetcher(ABC):
    def __init__(self, feed_name, config):
        self.feed_name = feed_name
        self.config = config

    @abstractmethod
    def get_new_feed_items(self):
        pass

class FilterSubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_score(self, item):
        pass

class SummarySubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_summary(self, item):
        pass

class DataStorageSubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

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

        # Use FeedManager to add feeds based on configuration
        for feed_name, feed_config in config['feeds'].items():
            self.feed_manager.add_feed(feed_name, feed_config)

        # Create SubsystemClient for each subsystem and store it
        for subsystem_name, subsystem_config in config['filter_subsystems'].items():
            self.subsystem_clients[subsystem_name] = FilterSubsystemClient(subsystem_config)

        self.subsystem_clients['DataStorage'] = DataStorageSubsystemClient(subsystem_config)
        self.subsystem_clients['Summary'] = SummarySubsystemClient(subsystem_config)


        logging.info("System started. Processing feeds at intervals of {} seconds.".format(config['processing_interval']))

        # Start continuous feed processing
        while True:
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
            # Check duplication
            if self.subsystem_clients['Duplication'].get_score(item) > config['duplication_threshold']:
                continue

            # Process other subsystems
            item['Summary'] = self.subsystem_clients['Summarization'].get_summary(item)
            item['Relevance'] = self.subsystem_clients['Relevance'].get_score(item)
            item['Quality'] = self.subsystem_clients['Quality'].get_score(item)
            item['Credibility'] = self.subsystem_clients['Credibility'].get_score(item)
            item['Freshness'] = self.subsystem_clients['Freshness'].get_score(item)

            # Store the processed feed item
            self.subsystem_clients['DataStorage'].store_item(item)
