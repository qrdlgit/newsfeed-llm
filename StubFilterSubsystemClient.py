from FilterSubsystemClient import FilterSubsystemClient
from utils import *
import logging

class StubFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        return 0
