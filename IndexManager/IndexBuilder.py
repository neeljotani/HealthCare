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

class IndexBuilder:

    unique_token_heading = set([])
    unique_token_text = set([])
    article_index_list = []
    weightage_settings = []

    def __init__(self):
        self.weightage_settings = list(db.weightage_settings.find())
        self.article_index_list = []
        # print(self.weightage_settings)


    def find_all_unique_tokens(self):
        for article_token in db.article_tokens.find():
            token_heading = article_token['token_heading']
            token_text = article_token['token_text']

            for single_token in token_heading:
                self.unique_token_heading.add(single_token)

            for single_token in token_text:

                self.unique_token_text.add(single_token)

    def check_article_in_index_list(self, article_id):
        article_obj = None
        for article_index in self.article_index_list:
            if article_id == article_index['article_id']:
                article_obj = article_index
                break;

        return article_obj

    def find_articles_from_tokens(self, input_tokens):
        article_ids = set([])
        for article_token in db.article_tokens.find({'_id': ObjectId('5e673cecc21e7db236f152d6')}):
            print(type(article_token))
            print("article Token :", article_token['token_text'])
            pass

        print('input tokens type :', type(input_tokens))
        print('input tokens : ', input_tokens)
        article_index_list = []
        for article_token in db.article_tokens.find():
            for input_token in input_tokens:
                if input_token in article_token['token_text']:
                    # print(input_token, 'token exists in article id ', article_token['article_id'])
                    # print((article_token['token_text']).get(input_token))
                    article_obj = self.check_article_in_index_list(article_token['article_id'])
                    if article_obj is None:
                        article_obj = {}

                        article_obj['article_id'] = article_token['article_id']
                        article_obj['weightage'] = self.get_weightage('tokens_text') * (article_token['token_text']).get(input_token)
                        self.article_index_list.append(article_obj)
                    else:
                        article_obj['article_id'] = article_token['article_id']
                        article_obj['weightage'] += self.get_weightage('tokens_text') * (article_token['token_text']).get(input_token)

                if input_token in article_token['token_heading']:
                    article_obj = self.check_article_in_index_list(article_token['article_id'])
                    if article_obj is None:
                        article_obj = {}

                        article_obj['article_id'] = article_token['article_id']
                        article_obj['weightage'] = self.get_weightage('tokens_heading') * (article_token['token_heading']).get(input_token)
                        self.article_index_list.append(article_obj)
                    else:
                        article_obj['article_id'] = article_token['article_id']
                        article_obj['weightage'] += self.get_weightage('tokens_heading') * (article_token['token_heading']).get(input_token)

        # self.article_index_list = article_index_list

    def update_click_weightage_of_articles(self):
        article_index_list = self.article_index_list
        for article_index in article_index_list:
            #print("weightage" ,article_index['weightage'])
            article_click_obj = db.article_clicks.find_one({'article_id': ObjectId(article_index['article_id'])})
            #print(article_click_obj)
            # article_index['article_id'] = article_token['article_id']
            article_index['weightage'] += self.get_weightage('clicks') * article_click_obj['click_count']
            #print("adding",self.get_weightage('clicks') * article_click_obj['click_count'])
            #article_index['weightage'] += 1

        self.article_index_list = article_index_list


    def update_share_weightage_of_articles(self):
        article_index_list = self.article_index_list
        for article_index in article_index_list:
            # print("weightage" ,article_index['weightage'])
            # article_click_obj = db.article_clicks.find_one({'article_id': ObjectId(article_index['article_id'])})
            article_shares_array = db.article_shares.find({'article_id': ObjectId(article_index['article_id'])})

            if True:
                for article_shares_obj in article_shares_array:
                    article_index['weightage'] += self.get_weightage('shares')

        self.article_index_list = article_index_list

    def update_like_weightage_of_articles(self):
        article_index_list = self.article_index_list
        for article_index in article_index_list:
            # print("weightage" ,article_index['weightage'])
            # article_click_obj = db.article_clicks.find_one({'article_id': ObjectId(article_index['article_id'])})
            article_likes_array = db.article_likes.find({'article_id': ObjectId(article_index['article_id'])})

            if True:
                for article_likes_obj in article_likes_array:
                    article_index['weightage'] += self.get_weightage('shares') * article_likes_obj['like_type']

        self.article_index_list = article_index_list

    def update_recommendation_weightage_of_articles(self):
        article_index_list = self.article_index_list
        for article_index in article_index_list:
            article_recommendations_array = db.article_recommendations.find({'article_id': ObjectId(article_index['article_id'])})

            if True:
                for article_recommendations_obj in article_recommendations_array:
                    article_index['weightage'] += self.get_weightage('recommendation')

        self.article_index_list = article_index_list

    def update_author_weightage_of_articles(self):
        article_index_list = self.article_index_list
        for article_index in article_index_list:
            article_obj = db.all_desease.find_one({'_id': ObjectId(article_index['article_id'])})

            if article_obj is not None:
                if article_obj['author_type'] == "admin":
                    article_index['weightage'] += self.get_weightage('author_admin')
                elif article_obj['author_type'] == "doctor":
                    article_index['weightage'] += self.get_weightage('author_doctor')

        self.article_index_list = article_index_list
    
    def get_article_in_index_list(self, article_id, article_index_list):
        for article in article_index_list:
            if article_id == article['article_id']:
                return article
        return None

    def update_article_in_index_list(self, article_obj, article_index_list):
        for article in article_index_list:
            if article_obj['article_id'] == article['article_id']:
                return article
        return None

    def get_weightage(self, weightage_of):
        for d in self.weightage_settings:
            if d['param'] == weightage_of:
                return d['weightage']
                break;

    def check_if_index_exists(self, token_string):
        index = None
        for article_index in db.article_index.find():
            if token_string == set(article_index['tokens']):
                print("index exists for ", token_string)
                index = article_index['index']
                break
        return index

    # to be removed :  below method is to init clicks of articles
    def init_clicks(self):
        for article in db.all_desease.find():
            print(article['document_title'])
            click_dict = {}
            click_dict['article_id'] = article['_id']
            click_dict['click_count'] = 0
            db.article_clicks.insert_one(click_dict)
        pass

    def start_building_index(self,token_string):
        index = self.check_if_index_exists(token_string)
        if index is None:
            # Indexing by tokens
            self.find_articles_from_tokens(token_string)
            #print("After Token Index article size", len(self.article_index_list))
            #print(self.article_index_list)

            # Indexing by clicks
            self.update_click_weightage_of_articles()
            #print("After update Index article size", len(self.article_index_list))
            #print(self.article_index_list)

            # Indexing by shares
            self.update_share_weightage_of_articles()
            #print("After share Index article size", len(self.article_index_list))
            #print(self.article_index_list)

            # Indexing by likes
            self.update_like_weightage_of_articles()
            #print("After like Index article size", len(self.article_index_list))
            #print(self.article_index_list)

            # Indexing by author
            self.update_author_weightage_of_articles()
            #print("After like Index article size", len(self.article_index_list))
            print(self.article_index_list)

            self.article_index_list = sorted(self.article_index_list, key=lambda i: i['weightage'],
                                                     reverse=True)

            article_index_dict = {}
            article_index_dict['tokens'] = list(token_string)
            article_index_dict['index'] = self.article_index_list

            db.article_index.insert_one(article_index_dict)

        else:
            self.article_index_list = index


# start_time = time.clock()
# indexBuilder = IndexBuilder()
# #indexBuilder.find_all_unique_tokens()
# inputStringProcessor = InputStringProcessor()
# token_string = inputStringProcessor.tokenize_input_string("I am having cough and headache");
# print('Token String : ', token_string)
#
# index = indexBuilder.check_if_index_exists(token_string)
#
# if index is None:
#     # Indexing by tokens
#     #indexBuilder.find_articles_from_tokens({'headache', 'cough'})
#     indexBuilder.find_articles_from_tokens(token_string)
#     print("After Token Index article size",len(indexBuilder.article_index_list))
#     print(indexBuilder.article_index_list)
#
#     # Indexing by clicks
#     indexBuilder.update_click_weightage_of_articles()
#     print("After update Index article size",len(indexBuilder.article_index_list))
#     print(indexBuilder.article_index_list)
#
#     # Indexing by shares
#     indexBuilder.update_share_weightage_of_articles()
#     print("After share Index article size",len(indexBuilder.article_index_list))
#     print(indexBuilder.article_index_list)
#
#     # Indexing by likes
#     indexBuilder.update_like_weightage_of_articles()
#     print("After like Index article size",len(indexBuilder.article_index_list))
#     print(indexBuilder.article_index_list)
#
#     # Indexing by author
#     indexBuilder.update_author_weightage_of_articles()
#     print("After like Index article size",len(indexBuilder.article_index_list))
#     print(indexBuilder.article_index_list)
#
#     indexBuilder.article_index_list = sorted(indexBuilder.article_index_list, key = lambda i: i['weightage'], reverse=True)
#     # print ("sorted", indexBuilder.article_index_list)
#
#     article_index_dict = {}
#     article_index_dict['tokens'] = list(token_string)
#     article_index_dict['index'] = indexBuilder.article_index_list
#
#     db.article_index.insert_one(article_index_dict)
#
#
# else:
#     indexBuilder.article_index_list = index
#
# print(indexBuilder.article_index_list)
# finish_time = time.clock()
# print("Total Indexing Time : ", (finish_time-start_time))
#indexBuilder.init_clicks()
