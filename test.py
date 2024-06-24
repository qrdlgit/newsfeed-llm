import utils,sys
db = utils.getSubsystem({"src":"SQLiteDataStorageSubsystem"})
v = utils.getSubsystem({"src":"VectorizeSubsystem", 'db':db})
print(sys.argv)
d = utils.getSubsystem({"src":sys.argv[1], "Vectorize":v, "db":db})

item = {"hash":"abc", "title":"title", "text":"text"}
item['Vectorize'] = v.get_vector(item)
method = getattr(d, sys.argv[2])
db.stop()
print(method(item))
