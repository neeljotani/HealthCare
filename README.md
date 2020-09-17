Main Logic

Search functionality is the heart of this application. Search is working on the concept of indexing. 

Approaches:
Search can be implemented two ways:

1) Crawl the data from Internet, apply cleaning functions and store that data in the Database
2) Crawl the tokens and URLs from Internet, store the references of tokens and give the external URLs in search results instead of URLs to internal data(articles)


We have followed first approach in this application. Though the second approach is easy in terms of logic, but second approach needs more computing power which cannot be possible by a personal device.

Below is the flow of first approach:

1) In the first approach we have crawled the articles from a source https://medicinenet.com and stored the data in the database
2) After that we have applied tokenizer and created tokens for each article.
3) Once the tokens are generated we store the token list and number of count of those tokens in a collection in Database.
4) After that whenever any user search something by entering phrases in search bar, we also convert that phrase into tokens and try to match the tokens we have already collected in step 3.
5) Now the main process of index building starts. In step 3, we have also captured number of particular tokens occurring in article, so whatever token we get from input string mentioned in step 4, we will match with tokens of article and create a list of articles of which the tokens matched.
6) We will sort this article list in descending order of occurrences of tokens. So that more token matched article will come first.
7) After that, we will add weightages of like/dislike, share, recommendations and clicks based on the weightage settings defined in database.
8) Once this list of article(index) is ready, we will store it in database first and then serve the results to the user.
9) Now if user enters the search phrase such a way that tokens from search query will be same, then we are not going to build index again. We will serve the results based on the stored index in previous step.
10) But if the tokens are new, then index building will run again. That means Index building is not one time process, it is continuous process. Every time Index will be evolved if users use it more and more.
 


There are few words/processes mentioned in above step are covered in details separate files:

1) How Crawler Works.docx : This file includes how we have gathered data of Medical terms from online website.

2) Database Design.docx: In above steps, most of the things are stored in database. Any applications’ data related performance depends on how the database design in made strong. This document contains detailed discussion on database design.

3) Module Wise Details.docx: Large applications are always developed by integrating different small modules. In this application also, different modules are integrated and data flows among those modules. This document contains details of all the modules with their significance and functionalities.

4) Tools and Technologies.docx : We have used various technology and to deal with those technologies, proper tools are needed. This document contains details of All the technologies, the reason why we are using that technology and the tools detailed including from where we can get those tools and technologies.

5) Project Setup.docx: Once getting/installing all tools and technologies, we need to setup project to develop/maintain/run the application. This document contains detailed information on how to setup each components of the application.

6) How To Test This Application.docx : Once the application is ready, we need to check if the application is running as per expectations. This document contains the information how to test each functionalities of the application.
