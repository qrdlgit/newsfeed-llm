from abc import ABC, abstractmethod
import sklearn.feature_extraction.text
import logging
import utils, sklearn.metrics.pairwise
import sentence_transformers
import gc, numpy as np
from scipy.sparse import csr_matrix, vstack
sm = sentence_transformers.SentenceTransformer("BAAI/bge-small-en-v1.5")

class VectorizeSubsystem(ABC):
    def __init__(self, config):
        self.config = config
        items = config['db'].get_items()
        self.vecs = [utils.decode(x['Vectorize']) for x in items]
        texts = [(x['title']+" "+x['text'])[:256] for x in items]
        self.items = [x['hash'] for x in items]
        self.tfidf_vecs = None
        if len(items) > 0:
            self.tfidf = sklearn.feature_extraction.text.TfidfVectorizer()
            self.tfidf_vecs = self.tfidf.fit_transform(texts)
            logging.info(f"Vectorizer tfidf shape {self.tfidf_vecs[0].shape}")
        gc.collect()

    def get_text(self,item):
        return item['title']+" "+item['text']

    def get_similarity_scores(self, item):
        ve = utils.decode(item['Vectorize'])
        se = sklearn.metrics.pairwise.cosine_similarity(self.vecs, [ve])[:,0]
        if False and self.tfidf_vecs is not None:
            vt = self.tfidf.transform([self.get_text(item)])
            st = sklearn.metrics.pairwise.cosine_similarity(self.tfidf_vecs, vt)[:,0]
            return (se+st)/2
        return se

    def get_vector(self, item):
        if item is None:
            return None
        v = None
        try:
            txt = item['text']
            v = sm.encode(txt[:256], show_progress_bar = False)
        except:
            v = np.full((384,),99999)
        self.items.append(item['hash'])
        self.vecs.append(v)
        if False and self.tfidf_vecs is not None:
            self.tfidf_vecs = vstack([self.tfidf_vecs, self.tfidf.transform([txt])])
        return utils.encode(v)
