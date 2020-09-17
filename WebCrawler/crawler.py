print("THis is crawler")

import csv
import requests
from lxml import etree

target_url = input('Which url is to be scraped?')

page = '''
<html>
<head>
</head>
    <body>
        <div>
            <h1 class="class_one">First heading</h1>
                <p>Some text</p>
            <div class="class_two">
                <div class="class_three">
                    <div class="class_one">
                        <center class="class_two">
                            <h3 class="class_three">
                            </h3>
                        </center>
                        <center>
                            <h3 class="find_first_class">
                                Some text
                            </h3>
                        </center>
                    </div>
                </div>
            </div>
            <div class="class_two">
                <div class="class_three">
                    <div class="class_one">
                        <center class="class_two">
                            <h2 class="find_second_class">
                            </h2>
                        </center>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
'''

#response = requests.get(target_url)
#document = etree.parse(response.content)
classes_list = ['find_first_class', 'find_second_class']
expressions = []

document = etree.fromstring(page)

for element in document.xpath('//*'):
    try:
        ele_class = element.xpath("@class")[0]
        print(ele_class)
        if ele_class in classes_list:
            tree = etree.ElementTree(element)
            expressions.append((ele_class, tree.getpath(element)))
    except IndexError:
        print("No class in this element.")
        continue

with open('test.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(expressions)