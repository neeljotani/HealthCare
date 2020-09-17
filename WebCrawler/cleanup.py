import time

from bson import ObjectId
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup
from pymongo import MongoClient
from WebCrawler import crawler1
import requests



client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()

blank_article_ids = []

def get_blank_articles():
    for blank_article in db.all_desease.find({'content':[]}):
        print(blank_article['document_title'])
        print(blank_article['content'])

        blank_article_ids.append(blank_article['_id'])
        pass

get_blank_articles()

print("Blank Article ID list : ", blank_article_ids)
print("total blank articles : ", len(blank_article_ids))

for article_id in blank_article_ids:
    print("deleting ", article_id)
    db.all_desease.delete_one({'_id': article_id})

# for article_id in blank_article_ids:
#     for blank_article in db.all_desease.find({'_id': article_id}):
#         print('blank article found : ', blank_article['document_title'])
#         article = crawler1.get_article_content(blank_article['source'], blank_article['url_title'])
#         pass
#     db.all_desease.update_one({"_id": article_id},
#                                              {"$set":
#                                                  {
#                                                      "content": article['content']
#                                                  }
#                                              })
#     pass
