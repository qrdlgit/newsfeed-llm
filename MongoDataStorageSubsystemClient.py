from pymongo import MongoClient
from FeedCLI import DataStorageSubsystemClient

class MongoDataStorageSubsystemClient(DataStorageSubsystemClient):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient(config["mongo_uri"])
        self.db = self.client[config["db_name"]]
        self.collection = self.db[config["collection_name"]]

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
