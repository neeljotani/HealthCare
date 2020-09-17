import nltk as nltk
from bson import ObjectId
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from pymongo import MongoClient
import time

from IndexManager.InputStringProcessor import InputStringProcessor

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()


class UserDBMethods:

    def __init__(self):
        pass

    def insert_user(self, fname, lname, email, password, user_type):
        inserted_id = 0
        user_dict = {"first_name": fname, "last_name": lname, "email": email,
                     "password": password, "user_type": user_type, "is_active": 1}

        inserted_id = db.users.insert_one(user_dict)
        return inserted_id

    def validate_credentials(self, email, password):
        user = None
        for u in db.users.find({'$and': [{'email': email}, {'password': password}, {'is_active': 1}]}):
            u['_id'] = str(u['_id'])
            user = u
        return user

    def validate_user(self, id, password):
        user = None
        for u in db.users.find({'$and': [{'_id': ObjectId(id)}, {'password': password}]}):
            u['_id'] = str(u['_id'])
            user = u
        return user

    def change_password(self, id, password):
        db.users.update_one({'_id': ObjectId(id)},
                                   {'$set': {'password': password}
                                    })
        return True

    def check_if_user_exists(self, email):
        user = None
        for u in db.users.find({'email': email}):
            user = u
        return user
