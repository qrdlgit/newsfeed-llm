from FilterSubsystemClient import FilterSubsystemClient

class QualityFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)

    def get_score(self, item):
        return item.get('quality_score', None)
