import math, pandas as pd, os, json, hashlib,datetime
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient                                                                                                                                    
from pymongo import MongoClient
import hashlib
from FeedCLI import *
import datetime
from datetime import timedelta
import logging
import bs4
import sys
sys.path.append('/home/tim/timl')
import nosql
import math
host = "https://clob.polymarket.com"
key = os.environ['POLY_KEY']
client = ClobClient(host, key=key, chain_id=POLYGON)
client.set_api_creds(client.create_or_derive_api_creds())
    

try:
    last_ts, tokens = pd.read_pickle("tokens.pkl")
except:
    last_ts, tokens = datetime.datetime.now().timestamp(), {}
    pd.to_pickle((datetime.datetime.now().timestamp(), tokens), "tokens.pkl")

all_orders = []

def bid_weight(price, alpha=10):
    return math.exp(-alpha * (1 - price))

def ask_weight(price, alpha=10):
    return math.exp(-alpha * price)




class PolyFeedFetcher(FeedFetcher):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient(config.get("mongo_uri", "mongodb://192.168.1.86"))
        self.db = self.client[config.get("db_name","wiki_jobs" )]
        self.collection = self.db[config.get("collection_name", "all_txts")]
        self.feed_weight = config.get('feed_weight', 1)
        self.seen_items = {}
        self.feed_url = config['feed_url']
        self.td = config.get('td', 300)
    
    def get_token_id(self, condId):
        if condId not in tokens:
            m = client.get_market(condition_id = condId)
            javier = m['tokens'][0]['token_id'] if m['tokens'][1]['outcome'] == 'No' else  m['tokens'][1]['token_id'] 
            tokens[condId] = (javier,0)
        return tokens[condId]

       
    def get_implied_from_book(order_book, prevPrice):
        order_book['bids'].insert(0,{'price':0, 'size':1})
        order_book['asks'].insert(0,{'price':100, 'size':1})

        weightedBidTotal = sum(float(bid['price']) * float(bid['size']) * bid_weight(float(bid['price'])) for bid in order_book['bids'])
        weightedAskTotal = sum(float(ask['price']) * float(ask['size']) * ask_weight(float(ask['price'])) for ask in order_book['asks'])
        weightedBidVolume = sum(float(bid['size']) * bid_weight(float(bid['price'])) for bid in order_book['bids'])
        weightedAskVolume = sum(float(ask['size']) * ask_weight(float(ask['price'])) for ask in order_book['asks'])
        if weightedBidVolume > 0 and weightedAskVolume > 0:
            weightedAvgBid = weightedBidTotal / weightedBidVolume
            weightedAvgAsk = weightedAskTotal / weightedAskVolume
            impliedTruePrice = (weightedAvgBid * weightedAskVolume + weightedAvgAsk * weightedBidVolume) / (weightedBidVolume + weightedAskVolume)
        else:
            impliedTruePrice = 0

        weightedImpliedPrice = impliedTruePrice
        
        flag = False
        newPrice = prevPrice
        if abs(weightedImpliedPrice - prevPrice) > 0.025:
            newPrice = weightedImpliedPrice
            flag = True
        
        #print("Weighted Implied Price:", weightedImpliedPrice)
        return weightedImpliedPrice, flag,prevPrice, weightedImpliedPrice - prevPrice, newPrice
    
    def get_implied(self, condId):
        global all_orders
        javier, prevPrice = self.get_token_id(condId)
        order_book = client.get_order_book(javier)
        order_book = json.loads(order_book.json)
        all_orders.append((condId,order_book))
        # Extract best bid and best ask
        wip, flag, prev, dif, newPrice = PolyFeedFetcher.get_implied_from_book(order_book, prevPrice)
        tokens[condId] = (javier, newPrice)
        return wip, flag, prev, dif

    def get_new_feed_items(self):
        global tokens
        try:
            last_ts, tokens = pd.read_pickle("tokens.pkl")
        except:
            last_ts, tokens = datetime.datetime.now().timestamp(), {}
        global all_orders
        nw = datetime.datetime.now().timestamp()
        df = nw - last_ts
        if df < self.td:
            logging.info(f"Not enough time has passed for poly check - {df}")
            return []
        else:
            pd.to_pickle((datetime.datetime.now().timestamp(), tokens), "tokens.pkl")
            new_feed_items = []
            ms = json.load(open("/media/tb/linux/txts/clob-client-dev/markets.json"))
            for m in ms:
                try:
                    price,flag,prev,dif = self.get_implied(m['condition_id'])
                    if flag:
                        entry_text = f"WeBoP: {m['title']} {'increased' if dif > 0 else 'decreased'} to {int(price*100)}c from {int(prev*100)}c"
                        entry_hash = hashlib.sha256(entry_text.encode()).hexdigest()
                        ts = datetime.datetime.now().timestamp()
                        item = {'hash':entry_hash, 'username':'poly', 'feed_type':'poly', 'feed_weight':1,
                            'text':entry_text, 'title':'price change for '+m['title'], 'link':m['title'], 'ts':ts}
                        new_feed_items.append(item)
                        logging.info(str(item))
                    else:
                        logging.info(f"{[m['title'],price, prev, dif]}")
                except Exception as e:
                    print("error", m['title'], e)
            nosql.nosql({"sqlite_path":"books.sql"}).insert_json(all_orders)
            all_orders = []
            pd.to_pickle((datetime.datetime.now().timestamp(), tokens), "tokens.pkl")
            return new_feed_items


