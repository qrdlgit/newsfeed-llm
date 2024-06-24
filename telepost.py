import MongoFeedFetcher, time, sys,os

def docmd(cmd):
    print(cmd)

n = MongoFeedFetcher.MongoFeedFetcher({'usernames':['jimcramer']})
while True:
    items = n.get_new_feed_items()
    for i in items:        
        txt = i['username']+":"+i['text']
        with open('/tmp/tele.txt', 'w') as f:
            f.write(txt)
        os.system("python telemsg.py /tmp/tele.txt")
        exit()
    time.sleep(1)
    
