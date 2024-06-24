from bs4 import BeautifulSoup
import importlib,logging
from typing import List, Dict
import numpy as np
from scipy.spatial.distance import cosine
import msgpack, msgpack_numpy,  base64

msgpack_numpy.patch()

def getSubsystem(config):
    module, class_ = None,None
    try:
        module = importlib.import_module(config['src'])
        class_ = getattr(module, config['src'])
        return class_(config)
    except Exception as e:
        logging.error(f'Failed to load Subsystem from config {config}: {module} {class_} {e}')
        return None


def keyword_density(text, keyword_weights):
    # Normalize text
    text = text.lower()

    # Count weighted occurrences of each keyword
    keyword_occurrences = sum(text.count(keyword) * weight for keyword, weight in keyword_weights.items())

    # Count total words
    total_words = len(text.split())

    # Calculate keyword density
    keyword_density = keyword_occurrences / total_words if total_words > 0 else 0

    return keyword_density

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    return soup.get_text()


def get_embedding(text, key, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   openai.api_key = key
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']


def encode(v):
    if v is None:
        return None
    b = msgpack.packb(v)
    return base64.b64encode(b).decode("utf-8")

def decode(b):
    if b is None:
        return None
    bd = base64.b64decode(b.encode("utf-8"))
    return msgpack.unpackb(bd)

def filter_by_cosine_similarity(items: List[Dict], comparison_vector: np.ndarray, threshold: float) -> List[Dict]:
    similar_items = []

    for item in items:
        item_vector = np.array(item['embed'])
        similarity = 1 - cosine(item_vector, comparison_vector)  # cosine returns distance, 1 - distance = similarity

        if similarity >= threshold:
            similar_items.append(item)

    return similar_items

