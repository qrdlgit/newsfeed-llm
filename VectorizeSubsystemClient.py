from abc import ABC, abstractmethod
import logging
import utils, sklearn.metrics.pairwise
import sentence_transformers
sm = sentence_transformers.SentenceTransformer("intfloat/e5-small-v2")

class VectorizeSubsystem(ABC):
    def __init__(self, config):
        self.config = config
        self.items = config['db'].get_items()
        self.vecs = [utils.decode(x['Vectorize']) for x in self.items]
                              
    @staticmethod
    def getSubsystem(config):
        return utils.getSubsystem(config)

    def get_similarity_scores(self, item):
        v = utils.decode(item['Vectorize'])
        return sklearn.metrics.pairwise.cosine_similarity(self.vecs, [v])[:,0]

    def get_vector(self, item):
        if item is None:
            return None
        v = None
        try:
            txt = item['title']+" "+item['text']
            v = sm.encode(txt[:256], show_progress_bar = False)
        except:
            v = np.full((384,),99999)
        self.items.append(item)
        self.vecs.append(v)
        return utils.encode(v)
