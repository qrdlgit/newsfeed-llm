from FilterSubsystemClient import FilterSubsystemClient
import oai
import utils
import numpy as np
embeds = []
class DuplicateFilterSubsystemClient(FilterSubsystemClient):
    def __init__(self, config):
        super().__init__(config)
        self.oai = config['oai']
        self.similarity_threshold = config['similarity_threshold']

    def get_score(self, item):
        item['embed'] = utils.get_embedding(item['text'], self.oai)
        embeds.append(item)
        #db.get_items()
        items = utils.filter_by_cosine_similarity(embeds, np.array(item['embed']), self.similarity_threshold)
        dupes = "\n".join([x['title'] for x in items])
        
        #print("\n\n", item['title'], "--:","\n", dupes,"\n\n")
        return 0
        #return oai.get_prompt(f"Here is a list of titles:\n{dupes}\n\n:"+dupes, config['oai'])
        return item.get('credibility_score', None)
