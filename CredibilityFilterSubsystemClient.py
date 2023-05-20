from FilterSubsystemClient import FilterSubsystemClient

class CredibilityFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        return item.get('credibility_score', None)
