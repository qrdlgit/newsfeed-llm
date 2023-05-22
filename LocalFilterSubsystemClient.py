from FilterSubsystemClient import FilterSubsystemClient
from utils import *
import logging

class LocalFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        density = keyword_density(item['text'], self.config['keyword_weights'][item['feed_type']])
        if density > 0:
            logging.info(f"LocalFilterSubsystemClient get_score {item['title']} = {density}")
        return density
