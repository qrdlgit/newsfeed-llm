import FeedCLI,utils, json,time
t = time.time()
db = utils.getSubsystem({'src':'SQLiteDataStorageSubsystem', 'flush_interval':999999})
items = db.get_items()
#['feed', 'feed_type', 'feed_weight', 'text', 'title', 'link', 'date', 'Local', 'Duplicate', 'Relevance', 
#'Quality', 'Credibility', 'Freshness']
r=[]
print(time.time() - t)
for x in items:
     print((x['title'], x['Duplicate'], utils.decode(x['Vectorize']).shape))
print(time.time() - t, len(items))
