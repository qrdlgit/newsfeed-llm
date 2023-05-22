from abc import ABC, abstractmethod
import logging
import importlib

class FilterSubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def getSubsystemClient(config):
        try:
            module = importlib.import_module(config['src'])
            class_ = getattr(module, config['src'])
            return class_(config)
        except Exception as e:
            logging.error(f'Failed to load FilterSubsystemClient from config {config}: {e}')
            return None

    @abstractmethod
    def get_score(self, item):
        pass
