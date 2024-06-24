import sqlite3
import queue,datetime
import threading
import time
from FeedCLI import DataStorageSubsystemClient
import logging, json

class SQLiteDataStorageSubsystemClient(DataStorageSubsystemClient):

    def __init__(self, config):
        super().__init__(config)
        self.db_path = config.get("sqlite_path", "stories.db")
        self.flush_interval = config.get("flush_interval",10)
        self.table_name = config.get("table_name","stories")
        self.del_hours = config.get("del_hours", 24*7)
        self.queue = queue.Queue()
        self.running = True
        self.create_table()
        if self.flush_interval < 10000:
            self.thread = threading.Thread(target=self._flush_queue)
            self.thread.start()
        
    def create_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        hash varchar(64) PRIMARY KEY,
                        json_column TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )  """
                )
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_timestamp ON {self.table_name}(timestamp)")
                conn.commit()
        except Exception as e:
            self.handle_error(e)

    def _flush_queue(self):
        while self.running:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    current_time = datetime.datetime.now()
                    threshold_time = current_time - datetime.timedelta(hours=self.del_hours)

                    # Delete old records
                    conn.execute(f"DELETE FROM {self.table_name} WHERE timestamp < ?", (threshold_time,))

                    # Insert new records from queue
                    if self.queue.qsize() > 0:
                        logging.info(f"inserting queue size: {self.queue.qsize()}")
                    while not self.queue.empty():
                        json_item = self.queue.get()
                        hashv = json_item['hash']
                        json_item = json.dumps(json_item)
                        cmd = f'''
                          INSERT INTO {self.table_name} (hash, json_column) values (?,?)
                          ON CONFLICT(hash) DO UPDATE SET 
                          json_column = excluded.json_column;
                        '''
                        conn.execute(cmd, (hashv, json_item,))
                    
                    conn.commit()
                    
                time.sleep(self.flush_interval)
            except Exception as e:
                self.handle_error(e)


    def store_item(self, item):
        # Serialize the item (which is a dictionary) to a JSON string
        self.queue.put(item)

    def handle_error(self, error):
        logging.error(f"An error occurred while storing item in SQLite: {error}")

    def get_items(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"SELECT json_column FROM {self.table_name}")
                items = [json.loads(row[0]) for row in cursor.fetchall()]
            return items
        except Exception as e:
            self.handle_error(e)
            return []

    def stop(self):
        self.running = False
        self.thread.join()



