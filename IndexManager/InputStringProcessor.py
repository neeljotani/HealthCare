import nltk as nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from pymongo import MongoClient
import collections

from IndexManager.tokenizer import Tokenizer

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()

class InputStringProcessor:

    def __init__(self):
        pass

    def tokenize_input_string(self, input_str):
        input_str_exists = False
        str_found = {}
        for str in db.input_string.find():
            if str['text'] == input_str:
                input_str_exists = True
                str_found = str
                break

        if not input_str_exists:
            db.input_string.insert_one({"text": input_str, "clicks": 0})
        else:
            str_found['clicks'] += 1
            db.input_string.update_one({"_id": str_found['_id']},
                                       {"$set":
                                           {
                                               "clicks": str_found['clicks'],
                                           }
                                       })

        tokenizer = Tokenizer()
        # set(tokenizer.clean_text(input_str).split())
        return set(tokenizer.clean_text(input_str).split())

    def index_lookup(self, input_tokens):
        tokens_found = False
        article_index_found = None
        for article_index in db.article_index.find():
            tokens_found = True
            if (article_index['tokens']).sort() == (list(input_tokens)).sort():
                article_index_found = article_index
                break

        if article_index_found is not None:
            print('article index found')
            pass
        else:
            article_index_element = {'tokens': list(input_tokens)}
            db.article_index.insert_one(article_index_element)
            pass


    def check_substring(self, str, sub_str):
        pass

# inputStringProcessor = InputStringProcessor()
# token_string = inputStringProcessor.tokenize_input_string("I am having cough and headache");
# print('Token String : ', token_string)

#inputStringProcessor.index_lookup(token_string)
