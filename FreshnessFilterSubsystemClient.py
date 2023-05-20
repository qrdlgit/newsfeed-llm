from FilterSubsystemClient import FilterSubsystemClient

class FreshnessFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        return item.get('freshness_score', None)
