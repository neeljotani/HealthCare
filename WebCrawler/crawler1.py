import time

from bson import ObjectId
from lxml import html
from lxml import etree
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests

article_url_list = []
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
alpha_url = 'https://www.medicinenet.com/diseases_and_conditions/alpha_<alphabet>.htm'

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()

def get_article_content(url, url_title):
    print('getting content of ', url_title)
    pageContent=requests.get(url)
    #time.sleep(6)
    tree = html.fromstring(pageContent.content)
    print(tree)

    article_dict = {"url_title":url_title}
    facts_processed = False
    titles = tree.xpath('//*[@id="headline"]/h1')
    # print('title tag = ', titles[0].tag)
    print('title text = ', titles[0].text)

    article_dict['document_title'] = titles[0].text

    #blocks = tree.xpath('//div[@class="wrapper"]/*/h3/span')
    content_arr = []
    blocks = tree.xpath('//div[@class="wrapper"]')
    facts_processed = False
    for block in blocks:
        myhtml = etree.tostring(block, pretty_print=True)
        #print("block html : ", myhtml)

        soup = BeautifulSoup(myhtml, 'lxml')
        sp = BeautifulSoup(myhtml, 'lxml')
        #temp_element = sp.find_next('p')

        #while (sp.find_next('p') or sp.find_next('ul')) is not None:
        #    print('parsing', sp.text)
        next_element = sp.next_element
        #print("next element",next_element)
        #while(next_element.text)


        content_dict = {}

        mytitle = soup.find('span')
        content_dict['text'] = ""
        if mytitle is not None:
            if "facts" in mytitle.text:
                facts_processed = True
                nxt = mytitle.find_next('ul')
                if nxt is not None:
                    # print("next elem:", nxt)
                    content_dict['text'] += str(nxt)

            if facts_processed:
                # print("Title : ", mytitle.text)
                content_dict['heading'] = mytitle.text


        para = soup.find_all('p')
        if para is not None:
            for p in para:
                if not p.text == "" and facts_processed:
                    # print("Content : ", p.text)
                    content_dict['text'] += p.text
                    nxt = p.find_next('ul')
                    if nxt is not None:
                        # print("next elem=", nxt)
                        content_dict['text'] += str(nxt)

        # li = soup.find_all('li')
        # if li is not None:
        #     data = "<ul>"
        #     for p in li:
        #         if not p.text == "" and facts_processed:
        #             print("Content : ", p.text)
        #             data += "<li>"+p.text+"</li>"
        #     content_dict['text'] = data + "</ul>"

        if facts_processed:
            if 'heading' in content_dict and 'text' in content_dict:
                if content_dict['heading'] != "" and content_dict['text'] != "":
                    content_arr.append(content_dict)

    article_dict['content'] = content_arr
    article_dict['keywords'] = {}
    article_dict['points'] = 0
    article_dict['source'] = url
    print("article dict", article_dict)
    #db.all_desease.insert_one(article_dict)
    return article_dict

def get_urls_from_alphabet():
    for alphabet in alphabets:
        pageContent = requests.get('https://www.medicinenet.com/diseases_and_conditions/alpha_'+alphabet+'.htm')
        tree = html.fromstring(pageContent.content)
        blocks = tree.xpath('//*[@id="AZ_container"]/div')
        for block in blocks:
            myhtml = etree.tostring(block, pretty_print=True)
            #print("block html : ", myhtml)

            soup = BeautifulSoup(myhtml, 'lxml')
            li_elements = soup.find_all('li')

            for li in li_elements:
                anchor_tag = li.find('a')
                print("href : ", anchor_tag.attrs['href'])
                print('title : ', anchor_tag.text)
                url_dict = {"title": anchor_tag.text, "href":anchor_tag.attrs['href'],"processed":False}
                db.urls_of_all_desease.insert_one(url_dict)


#get_article_content('https://www.medicinenet.com/bad_breath/article.htm','bad breath')
#get_article_content('https://www.medicinenet.com/adult-onset_asthma/article.htm', 'asthma')

#get_urls_from_alphabet()
count = 0
processed_count = 0
all_urls = db.urls_of_all_desease.find({'processed': False})
for url in all_urls:
    count += 1
    if url['processed'] is False:
        print(url['title'])
        db.all_desease.insert_one(get_article_content(url['href'], url['title']))
        print("article: ", url['title'], "inserted in DB successfully")
        db.urls_of_all_desease.update_one({"_id": url['_id']},
                                             {"$set":
                                                 {
                                                     "processed": True
                                                 }
                                             })
        #time.sleep(1)
        print('---------------------------------------------------------------------------------------')
        pass
    else:
        processed_count += 1
        pass
    pass
print("Total urls",count)
print("Processed urls", processed_count)
