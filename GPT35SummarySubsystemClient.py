from FeedCLI import *
import oai

class GPT35SummarySubsystemClient(SummarySubsystemClient):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_summary(self, item):
        return oai.get_prompt("Please return a summary of this with title, text and a link.  Text should be no more than 240 characters.  To summarize:"+item['text'], config['oai_key'])
