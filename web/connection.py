import sys
import os
import pymongo

# Get settings module

# Connect to mongo database
host = os.getenv('CONTEXT_MONGO_HOST', '127.0.0.1')
try:
    _conn = pymongo.Connection(host, 27017)
except AttributeError:
    _conn = pymongo.MongoClient(host, 27017)
_db = _conn['context']

# Mongo collections
_content = _db['content']
_cached_users = _db['cached_users']

# Ensure indicies
_content.ensure_index('url')
  
