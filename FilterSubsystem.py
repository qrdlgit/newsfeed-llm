from abc import ABC, abstractmethod
import logging
import utils

class FilterSubsystem(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_score(self, item):
        pass
