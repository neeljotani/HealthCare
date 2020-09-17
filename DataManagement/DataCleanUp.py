from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()

def init_author_type():
    for article in db.all_desease.find():
        db.all_desease.update_one({"_id": article['_id']},
                                                 {"$set":
                                                    {
                                                         "author_type": "admin"
                                                     }
                                                  })

# init_author_type()
