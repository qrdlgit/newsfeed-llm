from abc import ABC, abstractmethod
import logging
import utils

class FilterSubsystemClient(ABC):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def getSubsystemClient(config):
        return utils.getSubsystemClient(config)

    @abstractmethod
    def get_score(self, item):
        pass
