import time

from bson import ObjectId
from pymongo import MongoClient

from IndexManager.IndexBuilder import IndexBuilder
from IndexManager.tokenizer import Tokenizer

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()


def delete_all_indexes():
    x = db.article_index.delete_many({})
    print("Total Indexes deleted : ", x.deleted_count)
    pass


def reset_all_indexes():
    process_start_time = time.clock()
    tokenizer = Tokenizer()
    reset_token_start_time = time.clock()
    tokenizer.reset_tokens()
    reset_token_end_time = time.clock()
    print('Resetting tokens took time : ', reset_token_end_time - reset_token_start_time, 'seconds')

    # db.article_index.remove({})
    indexBuilder = IndexBuilder()
    for index in db.article_index.find():
        indexBuilder.article_index_list = []
        indexBuilder.start_building_index(index['tokens'])

    process_end_time = time.clock()
    print('Resetting Index took time : ', process_end_time - process_start_time, 'seconds')

    return process_end_time - process_start_time


## Call below method to delete all indexes built so far: DON'T DO THIS WITHOUT EXTREME REQUIRED
######## delete_all_indexes()

## Call below method to reset all indexes built so far: DON'T DO THIS WITHOUT EXTREME REQUIRED
reset_all_indexes()


