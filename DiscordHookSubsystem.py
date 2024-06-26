from abc import ABC, abstractmethod
import logging
import utils
import requests

class DiscordHookSubsystem(ABC):
    def __init__(self, config):
        self.config = config

    def get_score(self, item):
        try:
            content = item['title'][0:100]+":"+item['link']
            r = requests.post("https://discord.com/api/webhooks/1255384025007394877/nBARslhXt6uRNElD9fGPsmrh-pgA65FFXGGraUmJvJQ5qh0gaeEuWq6lLEvsXIrJFGIf", 
                              json = {"content":content})
            logging.info(f"Discord Response {content} {r.status_code}")
            return r.status_code
        except Exception as e:
            logging.error(f"Discord Error  {e}")



