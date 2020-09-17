import nltk as nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from pymongo import MongoClient

client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.healthcare_system
collections = db.collection_names()

class Tokenizer:
    def __init__(self):
        self.stemming = PorterStemmer()
        nltk.download('stopwords')
        nltk.download('punkt')
        self.stops = set(stopwords.words("english"))


    def apply_cleaning_function_to_list(self,X):
        cleaned_X = []
        for element in X.split():
            cleaned_X.append(self.clean_text(element))

        while "" in cleaned_X:
            cleaned_X.remove("")

        return set(cleaned_X)


    def clean_text(self, raw_text):
        """This function works on a raw text string, and:
            1) changes to lower case
            2) tokenizes (breaks down into words
            3) removes punctuation and non-word text
            4) finds word stems
            5) removes stop words
            6) rejoins meaningful stem words"""

        # Convert to lower case
        text = raw_text.lower()

        # Tokenize
        tokens = nltk.word_tokenize(text)
        # Keep only words (removes punctuation + numbers)
        # use .isalnum to keep also numbers
        token_words = [w for w in tokens if w.isalpha()]

        # Stemming
        #stemmed_words = [self.stemming.stem(w) for w in token_words]
        # Remove stop words
        meaningful_words = [w for w in token_words if not w in self.stops]

        # Rejoin meaningful stemmed words
        joined_words = (" ".join(meaningful_words))

        # Return cleaned data
        return joined_words

    def count_occurences(self, str, word_dict):
        output_dict = dict()
        # words = str.lower().split(" ")
        words = nltk.word_tokenize(str.lower())
        # search for pattern in a
        for given_word in word_dict:
            count = 0
            for i in range(0, len(words)):
                if given_word == words[i]:
                    count = count + 1
            output_dict[given_word] = count

        return output_dict

    def reset_tokens(self):
        delete_flag = db.article_tokens.delete_many({})
        print("delete flag :", delete_flag)
        articles = db.all_desease.find()
        count = 0
        for article in articles:
            print(article['url_title'])

            token_dict = {}
            token_dict['article_id'] = article['_id']

            all_title = article['url_title']
            all_text = ''
            for t in article['content']:
                all_title += t['heading'] + " "
                all_text += t['text'] + " "

            cleaned_text = self.apply_cleaning_function_to_list(all_title)
            count_dict = self.count_occurences(all_title, cleaned_text)
            token_dict['token_heading'] = count_dict

            cleaned_text = self.apply_cleaning_function_to_list(all_text)
            count_dict = self.count_occurences(all_text, cleaned_text)
            token_dict['token_text'] = count_dict
            token_dict['is_available'] = True

            db.article_tokens.insert_one(token_dict)
            count += 1

        print("Total : ", count, "articles have been processed for reset token")



tokenizer = Tokenizer()
# tokenizer.reset_tokens()

# input_text = "I have no read the novel on which \"The Kite Runner\" is based. My wife and daughter, who did, thought the movie fell a long way short of the book, and I'm prepared to take their word for it. But, on its own, the movie is good -- not great but good. How accurately does it portray the havoc created by the Soviet invasion of Afghanistan? How convincingly does it show the intolerant Taliban regime that followed? I'd rate it C+ on the first and B+ on the second. The human story, the Afghan-American who returned to the country to rescue the son of his childhood playmate, is well done but it is on this count particularly that I'm told the book was far more convincing than the movie. The most exciting part of the film, however -- the kite contests in Kabul and, later, a mini-contest in California -- cannot have been equaled by the book. I'd wager money on that."
# #input_text = "I am a java flu programmer."
# text_to_clean = input_text
#
# articles = db.all_desease.find()
# print(articles[0]['url_title'])
#
# all_title = articles[0]['url_title']
# all_text = ''
# for t in articles[0]['content']:
#     all_title += t['heading'] + " "
#     all_text += t['text'] + " "
#
# text_to_clean = all_title
# tokenizer = Tokenizer()
# cleaned_text = tokenizer.apply_cleaning_function_to_list(text_to_clean)
#
# print("input : ", text_to_clean)
# print("output : ", cleaned_text)
# count_dict = tokenizer.count_occurences(text_to_clean, cleaned_text)
#
# token_dict = {}
# token_dict['article_id'] = str(articles[0]['_id'])
# token_dict['token_heading'] = count_dict
# text_to_clean = all_text
# tokenizer = Tokenizer()
# cleaned_text = tokenizer.apply_cleaning_function_to_list(text_to_clean)
#
# print("input : ", text_to_clean)
# print("output : ", cleaned_text)
# count_dict = tokenizer.count_occurences(text_to_clean, cleaned_text)
# token_dict['token_text'] = count_dict
# token_dict['is_available'] = True
#
# db.article_tokens.insert_one(token_dict)

