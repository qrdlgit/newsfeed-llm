from FilterSubsystemClient import FilterSubsystemClient

class RelevanceFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        return item.get('relevance_score', None)
