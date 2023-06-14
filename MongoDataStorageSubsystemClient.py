from pymongo import MongoClient
from FeedCLI import DataStorageSubsystemClient

class MongoDataStorageSubsystemClient(DataStorageSubsystemClient):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient(config.get("mongo_uri", "mongodb://192.168.1.86"))
        self.db = self.client[config.get("db_name","newsfeeds" )]
        self.collection = self.db[config.get("collection_name", "feeditems")]

    def store_item(self, item):
        try:
            self.collection.insert_one(item)
        except Exception as e:
            self.handle_error(e)

    def handle_error(self, error):
        print(f"An error occurred while storing item in MongoDB: {error}")

    def get_items(self):
        try:
            items = list(self.collection.find())
            return items
        except Exception as e:
            self.handle_error(e)
            return []
