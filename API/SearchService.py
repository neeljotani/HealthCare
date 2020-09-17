import json
import os
import sys
import time

import path
from flask import Flask
from flask import request
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(os.path.abspath())
# print(sys.path)
# print(os.getcwd())
from Article.ArticleDBMethods import ArticleDBMethods
from User.UserDBMethods import UserDBMethods
from IndexManager.IndexBuilder import IndexBuilder
from IndexManager.InputStringProcessor import InputStringProcessor


app = Flask(__name__)
CORS(app)

@app.route('/getsearchresults', methods=['GET','OPTIONS'])
def get_search_results():
    print("is JSON? ", request.is_json)
    print("q", request.args['q'])
    print("p", request.args['p'])
    start_time = time.perf_counter()

    inputStringProcessor = InputStringProcessor()
    token_string = inputStringProcessor.tokenize_input_string(request.args['q']);

    indexBuilder = IndexBuilder()
    indexBuilder.start_building_index(token_string)

    articleDBMethods = ArticleDBMethods()
    articles = articleDBMethods.fetch_articles_from_index(indexBuilder.article_index_list, int(request.args['p']))

    response_obj = {}
    response_obj['articles'] = None


    finish_time = time.perf_counter()
    print("Total Indexing Time : ", (finish_time - start_time))

    total_no_of_articles = len(indexBuilder.article_index_list)
    return {"message": "Ok", "result_time": (finish_time - start_time), "articles": articles, "total_no_of_articles": total_no_of_articles}

@app.route('/clickarticle', methods=['GET','OPTIONS'])
def click_article():
    print("click_article() :: is JSON? ", request.is_json)
    print("id", request.args['id'])

    article_db_methods = ArticleDBMethods()
    article_db_methods.click_article_by_id(request.args['id'])

    return {"message": "Ok"}


@app.route('/getarticlebyid', methods=['GET','OPTIONS'])
def get_article_by_id():
    print("getarticlebyid() :: is JSON? ", request.is_json)
    print("id", request.args['id'])
    print("user_id", request.args['user_id'])

    article_db_methods = ArticleDBMethods()
    article_db_methods.click_article_by_id(request.args['id'])
    article_obj = article_db_methods.get_article_by_id(request.args['id'])
    like_count = article_db_methods.get_likes_of_acrticle(request.args['id'])
    dislike_count = article_db_methods.get_dislikes_of_acrticle(request.args['id'])
    like_obj = article_db_methods.get_like_by_user_and_article(request.args['id'], request.args['user_id'])
    share_count = article_db_methods.get_share_count_of_article(request.args['id'])
    recommend_count = article_db_methods.get_recommendation_count_of_acrticle(request.args['id'])
    recommend_obj = article_db_methods.get_recommend_by_user_and_article(request.args['id'], request.args['user_id'])

    if like_obj is None:
        liketype = 0
    else:
        liketype = like_obj['like_type']

    if recommend_obj is None:
        is_recommended = 0
    else:
        is_recommended = 1

    print({"message": "Ok", "likes":like_count, "dislikes": dislike_count, "liketype":liketype, "share_count":share_count, "recommend_count":recommend_count})
    return {"message": "Ok", "article": article_obj, "likes":like_count, "dislikes": dislike_count, "liketype":liketype,
            "share_count":share_count, "recommend_count":recommend_count, "is_recommended":is_recommended}

@app.route('/getinputstrings', methods=['GET','OPTIONS'])
def get_input_strings():
    print("get_input_strings() :: is JSON? ", request.is_json)
    # print("str", request.args['str'])

    article_db_methods = ArticleDBMethods()
    search_strings = article_db_methods.get_search_Strings(request.args['str'])

    # print(search_strings)
    return {"message": "Ok", "search_strings": search_strings}

@app.route('/likedislikearticle', methods=['POST','OPTIONS'])
def like_dislike_article():

    print("like_dislike_article() :: is JSON? ", request.is_json)
    print("article_id", request.values['article_id'])
    # content_dict = json.loads(json.dumps(request.get_json()))
    print("user_id", request.values['user_id'])
    print("liketype", request.values['liketype'])

    article_db_methods = ArticleDBMethods()
    like_obj = article_db_methods.update_like_by_user_and_article(request.values['article_id'], request.values['user_id'], request.values['liketype'])

    like_obj['_id'] = str(like_obj['_id'])
    like_count = article_db_methods.get_likes_of_acrticle(request.values['article_id'])
    dislike_count = article_db_methods.get_dislikes_of_acrticle(request.values['article_id'])

    return {"message": "Ok", "flag": 1, "like_count": like_count, "dislike_count": dislike_count, "like_obj": like_obj}

@app.route('/sharearticle', methods=['POST','OPTIONS'])
def share_article():
    print("share_article() :: is JSON? ", request.is_json)
    #content_dict = json.loads(json.dumps(request.get_json()))
    #print("user_id", content_dict['user_id'])
    print("article_id", request.values['article_id'])

    article_db_methods = ArticleDBMethods()
    article_db_methods.insert_share(request.values['article_id'])

    share_count = article_db_methods.get_share_count_of_article(request.values['article_id'])

    return {"message": "Ok", "flag": 1, "share_count": share_count}

@app.route('/recommendarticle', methods=['POST','OPTIONS'])
def recommend_article():
    print("recommend_article() :: is JSON? ", request.is_json)
    content_dict = json.loads(json.dumps(request.get_json()))
    print("user_id", request.values['user_id'])
    print("article_id", request.values['article_id'])

    article_db_methods = ArticleDBMethods()
    is_recommended = article_db_methods.update_recommend_by_user_and_article(request.values['article_id'], request.values['user_id'])

    recommend_count = article_db_methods.get_recommendation_count_of_acrticle(request.values['article_id'])

    return {"message": "Ok", "is_recommended": is_recommended, "recommend_count": recommend_count}


@app.route('/insertarticle', methods=['POST','OPTIONS'])
def insert_article():
    print("insert_article() :: is JSON? ", request.is_json)

    content_dict = json.loads(json.dumps(request.get_json()))

    article_db_methods = ArticleDBMethods()
    inserted_id = article_db_methods.insert_article(content_dict['heading'],content_dict['text'],content_dict['user_id'], content_dict['user_type'])

    if inserted_id != 0:
        return {"message": "Article saved successfully", "code": 1}
    else:
        return {"message": "Couldn't save Article. Please try again..", "code": 0}

@app.route('/updatearticle', methods=['POST','OPTIONS'])
def update_article():
    print("update_article() :: is JSON? ", request.is_json)

    content_dict = json.loads(json.dumps(request.get_json()))

    article_db_methods = ArticleDBMethods()
    inserted_id = article_db_methods.update_article(content_dict['id'], content_dict['heading'],
                                                    content_dict['text'], content_dict['user_id'],
                                                    content_dict['user_type'])

    if inserted_id != 0:
        return {"message": "Article saved successfully", "code": 1}
    else:
        return {"message": "Couldn't save Article. Please try again..", "code": 0}


@app.route('/getarticlelistbyuser', methods=['POST','OPTIONS'])
def get_article_list_by_user_id():
    print("insert_article() :: is JSON? ", request.is_json)

    content_dict = json.loads(json.dumps(request.get_json()))

    article_db_methods = ArticleDBMethods()
    article_list = article_db_methods.get_article_list_by_user(content_dict['user_id'])

    return {"message": "Article saved successfully", "code": 1, "article_list": article_list}

###################### User Related services ################################
@app.route('/registeruser', methods=['POST','OPTIONS'])
def register_user():
    print("register_user() :: is JSON? ", request.is_json)

    content_dict = json.loads(json.dumps(request.get_json()))

    user_db_methods = UserDBMethods()
    user_exists = user_db_methods.check_if_user_exists(content_dict['email'])

    if user_exists is not None:
        return {"message": "User already exists with same email id", "code": -1}
    else:
        inserted_id = user_db_methods.insert_user(content_dict['fname'],content_dict['lname'],content_dict['email'],
                                           content_dict['password'],content_dict['usertype'])

        if inserted_id != 0:
            return {"message": "Registration Successful", "code": 1}
        else:
            return {"message": "Couldn't register. Please try again..", "code": 0}


@app.route('/validateuser', methods=['POST','OPTIONS'])
def validate_user():
    print("validate_user() :: is JSON? ", request.is_json)
    # print("id", request.args['id'])
    content_dict = json.loads(json.dumps(request.get_json()))
    print("email", content_dict['email'])

    user_db_methods = UserDBMethods()
    user = user_db_methods.validate_credentials(content_dict['email'], content_dict['password'])

    if user is not None:
        del user['password']
        return {"message": "Ok", "code": 1, "user": user}
    else:
        return {"message": "Wrong email or password", "code": 0}

@app.route('/changepassword', methods=['POST','OPTIONS'])
def change_password():
    print("validate_user() :: is JSON? ", request.is_json)
    content_dict = json.loads(json.dumps(request.get_json()))

    user_db_methods = UserDBMethods()
    user = user_db_methods.validate_user(content_dict['id'], content_dict['password'])
    print(user)
    if user is not None:
        success = user_db_methods.change_password(content_dict['id'], content_dict['newpassword'])
        print("change password success : ", success)
        if success:
            return {"message": "Password Changed Successfully", "code": 1}
        else:
            return {"message": "Couldn't Change Password", "code": 0}
    else:
        return {"message": "Wrong current password", "code": 0}





##################### Run the Service ###############################
app.run(host='127.0.0.1', port=5000)


