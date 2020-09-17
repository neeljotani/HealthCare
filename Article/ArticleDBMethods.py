import nltk as nltk
from bson import ObjectId
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from pymongo import MongoClient
import re
import time

from IndexManager.InputStringProcessor import InputStringProcessor

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()


class ArticleDBMethods:

    def __init__(self):
        pass

    def fetch_articles_from_index(self, article_index, page_no):
        article_id_list = []
        articles = []
        if len(article_index) > 10:
            start_index = (page_no - 1) * 10;
            temp_end_index = start_index + 10
            if temp_end_index > len(article_index):
                end_index = start_index + len(article_index) % 10
            else:
                end_index = start_index + 10
        else:
            start_index = 0;
            end_index = len(article_index)

        for i in range(start_index, end_index):
            # for index in article_index:
            article_id_list.append(article_index[i]['article_id'])
            article = db.all_desease.find_one({'_id': ObjectId(article_index[i]['article_id'])})

            article['_id'] = str(article_index[i]['article_id'])
            try:
                article['content'] = article['content'][1]['text']
            except IndexError:
                article['content'] = article['content'][0]['text']
            article['content'] = article['content'][:250]
            article['content'] = str(article['content']).rsplit(' ', 1)[0]
            print("after ", article)
            articles.append(article)

        return articles

    def get_search_Strings(self, input_str):
        return_strings = []
        input_strings = db.input_string.find({'text': re.compile("^" + input_str, re.IGNORECASE)}).sort('clicks', -1)
        for str_obj in input_strings:
            obj = {}
            # obj['_id'] = str(str_obj['_id'])
            obj['text'] = str_obj['text']
            print("str_obj :", str_obj);
            return_strings.append(obj)
        return return_strings

    def click_article_by_id(self, article_id):
        article = None
        article = db.article_clicks.find_one({'article_id': ObjectId(article_id)})
        print('article click : article found : ', article)
        if article is None:
            click_dict = {'article_id': ObjectId(article_id), 'click_count': 1}
            db.article_clicks.insert_one(click_dict)
        else:
            db.article_clicks.update_one({'_id': article['_id']},
                                {'$set': {'click_count': article['click_count']+1}

                                 })


    def get_article_by_id(self, id):
        article = None
        print("type of id", type(id))
        article = db.all_desease.find_one({"_id": ObjectId(id)})

        if article != None:
            article['_id'] = str(article['_id'])

        return article

    def get_like_by_user_and_article(self, article_id, user_id):
        return db.article_likes.find_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})

    def update_like_by_user_and_article(self, article_id, user_id, like_type):
        like_obj = db.article_likes.find_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})

        if like_obj is None:
            like_dict = {'article_id': article_id, 'user_id': user_id, 'like_type': int(like_type)}
            inserted_id = db.article_likes.insert_one(like_dict)
        else:
            # like_obj['like_type'] = like_type
            print('updating like')
            if int(like_type) == like_obj['like_type']:
                new_like_type = 0
            else:
                new_like_type = like_type

            db.article_likes.update_one({'_id': like_obj['_id']},
                                {'$set': {'like_type': int(new_like_type)}

                                 })

        return db.article_likes.find_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})

    def get_likes_of_acrticle(self, article_id):
        results = db.article_likes.find({'$and': [{'article_id': article_id}, {'like_type': 1}]})
        print('like count', results.count());
        return results.count()

    def get_dislikes_of_acrticle(self, article_id):
        results = db.article_likes.find({'$and': [{'article_id': article_id}, {'like_type': -1}]})
        print('dislike count', results.count());
        return results.count()

    def insert_share(self, article_id):
        share_obj = db.article_shares.find_one({'article_id': article_id})

        if share_obj is None:
            share_dict = {'article_id': article_id, 'share_count': 1}
            inserted_id = db.article_shares.insert_one(share_dict)
        else:
            db.article_shares.update_one({'_id': share_obj['_id']},
                                {'$set': {'share_count': share_obj['share_count']+1}

                                 })

    def get_share_count_of_article(self, article_id):
        share_obj = None
        share_obj = db.article_shares.find_one({'article_id': article_id})

        if share_obj is not None:
            return share_obj['share_count']
        else:
            return 0

    def update_recommend_by_user_and_article(self, article_id, user_id):
        is_recommended = 0
        recommend_obj = db.article_recommendations.find_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})

        if recommend_obj is None:
            like_dict = {'article_id': article_id, 'user_id': user_id}
            inserted_id = db.article_recommendations.insert_one(like_dict)
            is_recommended = 1
        else:
            db.article_recommendations.delete_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})
            is_recommended = 0

        return is_recommended

    def get_recommend_by_user_and_article(self, article_id, user_id):
        return db.article_recommendations.find_one({'$and': [{'article_id': article_id}, {'user_id': user_id}]})

    def get_recommendation_count_of_acrticle(self, article_id):
        count = db.article_recommendations.count({'article_id': article_id})
        print('recommendation count', count);
        return count

    def insert_article(self, article_heading, article_text, user_id, user_type):
        article_obj = {}
        article_obj['url_title'] = article_heading
        article_obj['document_title'] = article_heading
        article_obj['points'] = 0
        article_obj['source'] = user_id
        article_obj['author_type'] = user_type
        article_obj['content'] = [{'heading':article_heading, 'text':article_text}]

        print(article_obj)
        db.all_desease.insert_one(article_obj)

    def update_article(self, article_id, article_heading, article_text, user_id, user_type):
        article_obj = {}
        article_obj['_id'] = article_id
        article_obj['url_title'] = article_heading
        article_obj['document_title'] = article_heading
        article_obj['points'] = 0
        article_obj['source'] = user_id
        article_obj['author_type'] = user_type
        article_obj['content'] = [{'heading':article_heading, 'text':article_text}]

        print(article_obj)
        #db.all_desease.insert_one(article_obj)
        db.all_desease.update_one({'_id': ObjectId(article_id)},
                                     {'$set': {'url_title': article_heading,
                                               'document_title': article_heading,
                                               'content': [{'heading':article_heading, 'text':article_text}]
                                               }
                                      })


    def get_article_list_by_user(self, user_id):
        return_article_list = []
        article_list = None
        article_list = db.all_desease.find({"source": user_id})

        if article_list is not None:
            for a in article_list:
                article = a
                article['_id'] = str(a['_id'])
                return_article_list.append(article)

        print("return article list",return_article_list)
        return return_article_list
# articleDBMethods = ArticleDBMethods()
# articleDBMethods.get_search_Strings("C")
# articleDBMethods.get_likes__of_acrticle('')
