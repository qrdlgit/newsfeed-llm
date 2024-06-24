import sys
sys.path.append('/home/tim/timl')
sys.path.append('/media/tb/linux/home/tim/openai/newsfeed-llm/')
import nosql
import PolyFeedFetcher
import json

al = nosql.nosql({"sqlite_path":"books.sql"}).get_items()
al.sort(key = lambda x:x[0])
prcs = {}
for a in al:
    for m in a[1]:
        c = m[0]
        book = m[1]
        if c not in prcs:
            prcs[c] = []
        prcs[c].append((a[0], PolyFeedFetcher.PolyFeedFetcher.get_implied_from_book(book,0)[0]))
print(json.dumps(prcs))

