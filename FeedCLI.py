import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from FilterSubsystem import FilterSubsystem
import importlib
import utils, gc,numpy as np, sys
import argparse
import os, sys

    
# Use Python's built-in logging module for logging
logging.basicConfig(filename='feed_processor.log', level=logging.DEBUG, format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s')

class FeedManager:
    def __init__(self):
        self.feed_fetchers = []

    def add_feed(self, config):
        # Create a FeedFetcher based on the feed type and configuration
        feed_fetcher = FeedFetcher.getFeedFetcher(config)
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
            src = config.get('src', 'RSSFeedFetcher')
            module = importlib.import_module(src)
            class_ = getattr(module, src)
            return class_(config)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            config['top'] = "--"
            config['seen_hashes'] = "--"
            logging.error(f'Failed to load FeedFetcher from config {config}: {e}')
            return None

    @abstractmethod
    def get_new_feed_items(self):
        pass

class SummarySubsystem(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_summary(self, item):
        pass

class DataStorageSubsystem(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def store_item(self, item):
        pass

    @abstractmethod
    def handle_error(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class FeedCLI:
    subs_score = ['Relevance','Quality', 'Credibility', 'Freshness']

    def __init__(self):
        self.feed_manager = FeedManager()
        self.subsystems = {}

    def stop_system(self):
        self.db.stop()

    #@profile
    def start_system(self):
        parser = argparse.ArgumentParser(description='Example script to demonstrate argument parsing.')
        #parser.add_argument('pos_arg', type=int, help='A positional argument')
        parser.add_argument('--settings', type=str, default="settings.json", help='JSON settings configuration file to use')
        args = parser.parse_args()

        # Load configuration from settings.json
        with open(args.settings) as file:
            config = json.load(file)

        self.db = utils.getSubsystem(config['db_subsystem'])
        if self.db is None:
            return
        
        items = self.db.get_items()
        seen_hashes = {x['hash']:True for x in items}
        config['Vectorize']['db'] = self.db

        t = time.time()
        vectS = utils.getSubsystem(config['Vectorize'])
        logging.info(f"Intialized vectorizer: {time.time() - t}s")

        if vectS is None:
            self.stop_system()
            return
        
        self.subsystems['DataStorage'] = self.db
        self.subsystems['Vectorize'] = vectS

        # Use FeedManager to add feeds based on configuration
        feed_count = config.get('feed_count',-1)
        count = 0
        for feed_config in config['feeds']:
            feed_config['top'] = config
            feed_config['db'] = self.db
            feed_config['seen_hashes'] = seen_hashes
            self.feed_manager.add_feed(feed_config)
            count = count + 1
            if count > feed_count:
                break
        logging.info(f"feeds added {len(self.feed_manager.get_feeds())}")

        self.post_systems = config.get("post_systems", [])
        # Create Subsystem for each subsystem and store it
        for subsystem_config in config['subsystems']:
            subsystem_config['db'] = self.db
            subsystem_config['Vectorize'] = vectS
            subsys = utils.getSubsystem(subsystem_config)
            name = subsystem_config['name']
            logging.info(f"adding subystem {name} = {str(subsys)}")
            self.subsystems[name] = subsys

        proc_interval = config.get('processing_interval', 300)
        min_proc_interval = config.get('min_processing_interval', 1)
        thread_timeout = config.get('thread_timeout', 120)
        logging.info("System started. Processing feeds at intervals of {} seconds.".format(proc_interval))

        # Start continuous feed processing
        threads = {}

        for i in range(100):
            logging.info(f"Looping {i}")
            t = time.time()
            for feed_fetcher in self.feed_manager.get_feeds():
                # Create a new thread for processing each feed
                furl = feed_fetcher.feed_url
                if furl not in threads or not threads[furl].is_alive():
                    thread = threading.Thread(target=self.process_feed, args=(feed_fetcher, config,))
                    thread.name = furl 
                    thread.start()
                    threads[furl] = thread
            
            deadline = time.time() + thread_timeout

            while any(thread.is_alive() for thread in threads.values()) and time.time() < deadline:
                for thread in threads.values():
                    thread.join(timeout=max(1, deadline - time.time()))
            
            threads = {url: thread for url, thread in threads.items() if thread.is_alive()}
            live_threads = len(threads)
            # Delay before the next loop iteration
            gc.collect()
            slp_time = max(proc_interval - (time.time() - t), min_proc_interval)
            logging.info(f"Got feeds, {live_threads} live threads left over, sleeping for {slp_time}")
            time.sleep(slp_time)
        self.stop_system()

    def process_feed(self, feed_fetcher, config):
        try:
            self.process_feed_try(feed_fetcher, config)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            logging.error(f"Error with {feed_fetcher.feed_url}: {e}")

    def process_feed_try(self, feed_fetcher, config):
        # Get new feed items
        items = feed_fetcher.get_new_feed_items()
        systs = ['Local','Duplicate','Vectorize']
        localS,dupeS,vectS = [self.subsystems.get(x, None) for x in systs]

        #store everything, but filter progressively until publishable to agg feed
        for item in items:
            #customizable local to fast fail
            local_score = None if localS is None else localS.get_score(item)
            item['Local'] = local_score
            
            if local_score and local_score > config['local_threshold']:
                self.subsystems['DataStorage'].store_item(item)
                continue
            
            #needed for filters
            item['Vectorize'] = vectS.get_vector(item) 
            
            dupe_score = None if dupeS is None else dupeS.get_score(item)
            item['Duplicate'] = dupe_score
            
            if dupe_score and dupe_score > config['duplicate_threshold']:
                self.subsystems['DataStorage'].store_item(item)
                continue

            # Process other subsystems
            # item['Summary'] = self.subsystems['Summary'].get_summary(item)
            for ss in FeedCLI.subs_score:
                subs = self.subsystems.get(ss, None)
                item[ss] = None if subs is None else subs.get_score(item)

            for ss in self.post_systems:
                subs = self.subsystems.get(ss, None)
                logging.info(f"post system {subs} {ss} ")
                item[ss] = None if subs is None else subs.get_score(item)
                logging.info(f"post system2 {subs} {ss} {item[ss]}")

            # Store the processed feed item
            self.subsystems['DataStorage'].store_item(item)


if __name__ == "__main__":
    feed = FeedCLI()
    try:
        feed.start_system()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print("Error starting system", e)
        feed.stop_system()

