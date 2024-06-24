import utils,numpy as np
import FilterSubsystem

class SimpleDuplicateFilterSubsystem(FilterSubsystem.FilterSubsystem):
    def __init__(self, config):
        super().__init__(config)
        pass

    def get_score(self, item):
        scores = self.config['Vectorize'].get_similarity_scores(item)
        indices = np.argsort(scores)
        mx, mx2 = indices[-1],indices[-2]
        #this is because we want to ignore ourself, which is going to be 1
        #logical coupling, but alternatives are awkward
        #print(scores[mx], scores[mx2])
        if scores[mx] > 0.9999:
            return float(scores[mx2])
        else:
            return float(scores[mx])

