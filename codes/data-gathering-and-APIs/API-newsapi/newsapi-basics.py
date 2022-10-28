
import requests
import json
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

#-----------------------------------------------------
#USER PARAM
#-----------------------------------------------------
read_file=False     #if false then pull from newsapi
file_name="2021-09-24-H12-M20-S09-newapi-raw-data.json" #ignored if read_file=False

baseURL = "https://newsapi.org/v2/everything?"
total_requests=2
verbose=True

API_KEY='INSERT_API_KEY'
TOPIC='coffee'


#-----------------------------------------------------
#READ JSON OR GET DICTIONARY FROM CLOUD
#-----------------------------------------------------

#READ FILE INTO DICTIONARY 
if(read_file):
    with open(file_name) as f:
        response = json.load(f)

#GET DATA FROM CLOUD
else:
    URLpost = {'apiKey': API_KEY,
               'q': '+'+TOPIC,
               'sortBy': 'relevancy',
               'totalRequests': 1}

    #GET DATA FROM API
    response = requests.get(baseURL, URLpost) #request data from the server
    # print(response.url); exit()
    response = response.json() #extract txt data from requests

    #GET TIMESTAMP FOR PULL REQUEST
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d-H%H-M%M-S%S")

    with open(timestamp+'-newapi-raw-data.json', 'w') as outfile:
        json.dump(response, outfile, indent=4)

#-----------------------------------------------------
#FUNCTION TO CLEAN STRINGS
#-----------------------------------------------------
def string_cleaner(input_string):
    try: 
        out=re.sub(r"""
                    [,.;@#?!&$-]+  # Accept one or more copies of punctuation
                    \ *           # plus zero or more copies of a space,
                    """,
                    " ",          # and replace it with a single space
                    input_string, flags=re.VERBOSE)

        #REPLACE SELECT CHARACTERS WITH NOTHING
        out = re.sub('[’.]+', '', input_string)

        #ELIMINATE DUPLICATE WHITESPACES USING WILDCARDS
        out = re.sub(r'\s+', ' ', out)

        #CONVERT TO LOWER CASE
        out=out.lower()
    except:
        print("ERROR")
        out=''
    return out

#-----------------------------------------------------
#CLEAN DATA AND MAKE A LIST OF LISTS
#-----------------------------------------------------
article_list=response['articles']   #list of dictionaries for each article
article_keys=article_list[0].keys()
print("AVAILABLE KEYS:")
print(article_keys)
index=0
cleaned_data=[];  
for article in article_list:
    tmp=[]
    if(verbose):
        print("#------------------------------------------")
        print("#",index)
        print("#------------------------------------------")

    for key in article_keys:
        if(verbose):
            print("----------------")
            print(key)
            print(article[key])
            print("----------------")

        if(key=='source'):
            src=string_cleaner(article[key]['name'])
            tmp.append(src) 

        if(key=='author'):
            author=string_cleaner(article[key])
            #ERROR CHECK (SOMETIMES AUTHOR IS SAME AS PUBLICATION)
            if(src in author): 
                print(" AUTHOR ERROR:",author);author='NA'
            tmp.append(author)

        if(key=='title'):
            tmp.append(string_cleaner(article[key]))

        # if(key=='description'):
        #     tmp.append(string_cleaner(article[key]))

        # if(key=='content'):
        #     tmp.append(string_cleaner(article[key]))

        if(key=='publishedAt'):
            #DEFINE DATA PATERN FOR RE TO CHECK  .* --> wildcard
            ref = re.compile('.*-.*-.*T.*:.*:.*Z')
            date=article[key]
            if(not ref.match(date)):
                print(" DATE ERROR:",date); date="NA"
            tmp.append(date)

    cleaned_data.append(tmp)
    index+=1

#-----------------------------------------------------
#CONVERT TO PANDAS DATA FRAME AND WRITE TO CSV
#-----------------------------------------------------
df = pd.DataFrame(cleaned_data)
print(df)
df.to_csv('cleaned.csv', index=False) #,index_label=['title','src','author','date','description'])

