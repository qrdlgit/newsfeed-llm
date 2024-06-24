import pymongo,time,json,dateutil
client = pymongo.MongoClient('192.168.1.86', 27017)
import hashlib,jsonpath
feeds_mongo = client.wiki_jobs.feeds
all_txts = client.wiki_jobs.all_txts
import sentence_transformers
from bs4 import BeautifulSoup, SoupStrainer

def log(txt):
    with open("/media/tb/linux/gather.log","a") as f:
        f.write(txt+"\n")
        
try:
    if sm == None:
        raise Exception
except:
    sm = sentence_transformers.SentenceTransformer("BAAI/bge-small-en-v1.5")
import RSSFeedFetcher
import importlib,time,pymongo,datetime
importlib.reload(RSSFeedFetcher)
count=0
def get_rss_feeds():
    fcfg = json.load(open("settings.json","r"))
    t = time.time()
    from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne
    client = pymongo.MongoClient('192.168.1.86', 27017)
    feeds_mongo = client.wiki_jobs.feeds
    count=0
    import joblib
    def get_feed(f):
        global count    
        rsf = f
        added = rsf.get_new_feed_items()
        count=count+1
        cnt = feeds_mongo.count_documents({})
        log(f'{f.feed_url,cnt, "added", added, "count", count}')
    joblib.Parallel(n_jobs=32, timeout=120, prefer='threads')(joblib.delayed(get_feed)(f) for f in feeds)

import os,datetime,msgpack, zlib

import pymongo

client = pymongo.MongoClient('192.168.1.86', 27017)
all_feeds_mongo = client.wiki_jobs.all_feeds
import msgpack,datetime

def comp(mj):
    if mj['c']=='z':
        mj['d'] = zlib.compress(msgpack.packb(mj['d']))

def decomp(mj):
    if mj['c']=='z':
        mj['d'] = msgpack.unpackb(zlib.decompress(mj['d']))


def persist(src, msg):
    log(f"prst:{src,len(msg)}")
    t = round(datetime.datetime.now().timestamp())
    feed = {"s":src, "c":"z", "t":t, "d":msg}
    comp(feed)
    all_feeds_mongo.insert_one(feed)
    print('inserted', len(feed))

def read_persist(directory, persistf):
    # Loop through all files in the specified directory
    for filename in os.listdir(directory):
        # Construct the full file path
        filepath = os.path.join(directory, filename)
        
        # Check if it is a file (and not a directory)
        if os.path.isfile(filepath):
            # Extract prefix from the filename
            prefix = filename.split('_')[0] + '_'
            
            # Read data from the file
            with open(filepath, 'r') as file:
                data = file.read()
            
            # Call the persist function
            persistf(prefix, data)
            
            # Delete the file
            os.remove(filepath)

read_persist("/home/tim/mitm/msgs", persist)

#feeds_mongo = client.wiki_jobs.texts
'''
_id, hash
txt, title + first [:256]
ts - entrydate.timestamp()
vec
src - src (for feeds)
'''


def parse_forexfactory(f):   
    txt = msgpack.unpackb(zlib.decompress(f['d']))
    soup = BeautifulSoup(txt, 'lxml')
    vs = soup.find_all("li", {"class": "flexposts__item"})
    rv = []
    for item in vs:
        user = item.find("div", {"class": "flexposts__storydisplay"})
        if user is not None:
            user = user.find('a')
            u=user.contents[0]
        else:
            continue
        a = item.find('a')
        if a is not None:
            href = a.get('href')
            title = a.get('title')
            txt= a.text +" "+title
            hash = hashlib.sha256(txt.encode()).hexdigest()
            ts = round(datetime.datetime.now().timestamp())
            rv.append({'_id':hash, 'txt':txt, 'src':'forexfactory', 'u':u, 'ts':ts})
    return rv
        
def parse_reddit(f):
    txt = msgpack.unpackb(zlib.decompress(f['d']))
    soup = BeautifulSoup(txt, 'lxml')
    v = soup.find_all(["h3", "a"])
    import json
    flag = False
    vs = []
    pair = []
    for i in v:
        if i is None:
            continue
        if i.name == "h3":
            pair.append(i.get_text())
        if (i.name=="a" and len(i.get_text()) > 2 and i.get_text()[:2]=="u/"):
            if len(pair) == 0:
                break
            else:
                pair.append(i.get_text())
                vs.append(pair)
                pair = []
    rv = []
    for p in vs:
        txt = p[0]
        hash = hashlib.sha256(txt.encode()).hexdigest()
        u = p[1]
        ts = round(datetime.datetime.now().timestamp())
        rv.append({'_id':hash, 'txt':txt, 'src':'reddit', 'u':u, 'ts':ts})
    return rv
    

def parse_twitter(f):
    log("parsing twitter------")
    msg = msgpack.unpackb(zlib.decompress(f['d']))
    j = json.loads(msg)
    print("parse_twitter: found", len(j))
    #print(json.dumps(j))
    try:
        vs = jsonpath.jsonpath(j, 'data.home.home_timeline_urt.instructions.*.entries.*')
        if type(vs) == bool:
            vs = jsonpath.jsonpath(j, 'data.*.*.*.*.*.entries.*')
    except Exception as e:
        print("vs", e, vs)
    print("found:", len(vs))
    tweets = []
    def find(key, st,end,stop=False):
        rv = []
        for i in range(st,end):
            pth = '.'.join(['*']*i+[key])
            vse = jsonpath.jsonpath(ent, pth)#.content')#.itemContent')#.tweet_results.core')
            if vse:
                rv.append(vse[0])
                if stop:
                    break
        return rv
    for ent in vs:
        tweet = []
        ft = find('full_text', 4,15)
        sn = find('screen_name', 4,15, stop=True)
        ts = find('created_at', 4,15, stop=True)
        if len(sn) == 0 or len(ft)==0:
            continue
        tweets.append([sn[0],ts,ft])
    rv = []
    for tweet in tweets:
        txt = " ".join(tweet[2])
        hash = hashlib.sha256(txt.encode()).hexdigest()
        u = tweet[0]
        ts = round(dateutil.parser.parse(tweet[1][0]).timestamp())
        rv.append({'_id':hash, 'txt':txt, 'src':'twitter', 'u':u, 'ts':ts})
    log(f"twitter {len(msg)} {len(vs)} {len(tweets)} {len(rv)}")    
    return rv
    
def parse_feeds(f):
    txt = f['title']+" "+f['text']
    txt = txt[:256]
    hash = hashlib.sha256(txt.encode()).hexdigest()
    ts = round(f['entry_date'].timestamp())
    src = 'feeds'
    user = f['link']
    item = {'_id':hash, 'txt':txt, 'src':src, 'u':user, 'ts':ts}
    return [item]

def parse_discord(f):
    d = json.loads(msgpack.unpackb(zlib.decompress(f['d'])))['d']
    try:
        txt = d['content']
    except:
        return None
    txt = txt[:256]
    ts = round(dateutil.parser.parse(d['timestamp']).timestamp())
    hash = hashlib.sha256(txt.encode()).hexdigest()
    src = 'discord'
    u = d['author']['username']
    item = [{'_id':hash, 'txt':txt, 'src':src, 'u':u, 'ts':ts}]
    return  item
def parse_reuters(f):
    d = json.loads(msgpack.unpackb(zlib.decompress(f['d'])))
    edges = []
    items = []
    try:
        edges = d['data']['feed']['edges']
    except:
        pass
    for e in edges:
        txt = e['node']['title']+": "+e['node']['description']
        ts = datetime.datetime.now().timestamp()
        hash = hashlib.sha256(txt.encode()).hexdigest()
        src = 'reuters'
        u = 'reuters'
        item = {'_id':hash, 'txt':txt, 'src':src, 'u':u, 'ts':ts}
        items.append(item)
    return  items
    
def filter_caps(fenum,  parserf):
    log(f"filtering {parserf}")
    fc = 0
    flag = False
    try:
        items = []
        fenum = list(fenum)
        print("filter_caps Found: ", len(fenum))
        for i,f in enumerate(fenum):

            flag = True
            items = parserf(f)
            if items is None:
                continue
            print("processing items len", len(items))
            for item in items:
                if item is None:
                    continue
                try:
                    g = all_txts.find({'_id':item['_id']}).next()
                    vec = g['vec']
                    item['ts'] = g['ts']
                except:
                    print("excpted")
                    fc += 1
                    vec = msgpack.packb(sm.encode(item['txt']))   
                item['vec'] = vec
                all_txts.replace_one({'_id':item['_id']}, item, upsert=True)
        if flag:
            log(f"{parserf} found {len(items)} added {fc}")
        else:
            log(f"{parserf} none found")
    except Exception as e:
        print("filter_caps error", e)
        log(f"{parserf} error - {e}")

def gather():
    print("cycling", datetime.datetime.now(), end="..",flush=True)
    ts = round((datetime.datetime.now() - datetime.timedelta(minutes=10)).timestamp())
    print("timestamp", ts, end="..",flush=True)
    read_persist("/home/tim/mitm/msgs", persist)
    #try:
    #    get_rss_feeds()
    #except Exception as e:
    #    log(f"get_rss_feeds error: {e}")
    #filter_caps(feeds_mongo.find({'entry_date':{'$gt':datetime.datetime.now() - datetime.timedelta(minutes=15)}}), parse_feeds)
    print("filtering", end="..",flush=True)

    #filter_caps(all_feeds_mongo.find({'s':'reuters_', 't':{'$gt':ts}}), parse_reuters)
    #filter_caps(all_feeds_mongo.find({'s':'discord_', 't':{'$gt':ts}}), parse_discord)
    filter_caps(all_feeds_mongo.find({'s':'twitter_', 't':{'$gt':ts}}), parse_twitter)
    #filter_caps(all_feeds_mongo.find({'s':'reddit-politics_', 't':{'$gt':ts}}), parse_reddit)
    #filter_caps(all_feeds_mongo.find({'s':'reddit-geopolitics_', 't':{'$gt':ts}}), parse_reddit)
    #filter_caps(all_feeds_mongo.find({'s':'forexfactory_', 't':{'$gt':ts}}), parse_forexfactory)
    print("done",flush=True)

while True:
    try:
        gather()
    except Exception as e:
        print(e, flush=True)
        break
    time.sleep(0.1)
    
