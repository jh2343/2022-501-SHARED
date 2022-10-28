# NOTE: THE REDUNDANT IMPORTS AND FUNCTION DEFINITIONS IS INTENTIONAL TO MAKE THE CODE CELLS SELF CONTAINED 
import json
from logging import raiseExceptions 
import tweepy
import time
from datetime import datetime
import time
import os

# PRINT TWEEPY VERSION
print("tweepy version =",tweepy.__version__)

#----------------------
# READ API KEY FILE
#----------------------
f = open("api-keys.json")
input=json.load(f); #print(input)

# LOAD KEYS INTO API
consumer_key=input["consumer_key"]    
consumer_secret=input["consumer_secret"]    
access_token=input["access_token"]    
access_token_secret=input["access_token_secret"]    
bearer_token=input["bearer_token"]    

#----------------------
# DEFINE USEFUL FUNCTIONS
#----------------------

# DEFINE PRETTY PRINT JSON FUNCTION
def pretty_print_json(input):
    print(json.dumps(input, indent=4))

# DEFINE FUNCTION TO SAVE TWEEPY SEARCH RESULTS
#   searches=array with various tweepy search objects
#   TODO: ADD "full and sparse" mode
#          full = save all tweet data (100 tweeks ~ 1 MB  --> 100,000 ~ 1 GB)
#          sparse = only save most important info
def save_search_tweets_results(searches,info_str="",output_name="tweet-search.json"):
    # if(str(type(input)) == "<class 'tweepy.models.SearchResults'>"):
    if(str(type(searches)) == "<class 'list'>"):
        #COMBINE ALL JSONS FOR VARIOUS TWEETS INTO ON BIG JSON CALL "out"
        out={}
        out["search_info"]=info_str

        #LOOP OVER SEARCHES
        tweet_ids=[]
        k=0 #counter
        for search in searches:
            #LOOP OVER TWEETS IN SEARCH
            for i in range(0,len(search)):
                out[str(k)]=search[i]._json
                tweet_id=search[i]._json["id_str"]
                #CHECK FOR REDUNDANT TWEETS
                if tweet_id in tweet_ids:
                    print("WARNING: REPEATED TWEETS IN SAVED FILE; ID = ",tweet_id)
                tweet_ids.append(search[i]._json["id_str"])

                k+=1
            #pretty_print_json(out)

        #DELETE FILE IF IT EXIST (START FRESH)
        if os.path.exists(output_name):
            os.remove(output_name)

        #WRITE FILE
        with open(output_name, 'w') as f:
            json.dump(out, f)
    else: 
        raise RuntimeError("ERROR: Incorrect datatype")

#----------------------
# SET UP CONNECTION
#----------------------
#   Use special options when initializing the API. These tell
#   it to wait while the Twitter time-limit windows elapse
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True) 

#----------------------
# RUN SEARCH 
#----------------------

#SEARCH PARAM
query="Trump OR Mar-a-Lago OR Donald"

# NUMBER OF TWEETS TO SEARCH 
# number_of_tweets=1000 
number_of_tweets=18000*2 
# ideally use multiples of 100 for number_of_tweets
# should be able to collect 18000 tweets every 15 minutes
start_time = time.time()
max_loop_time_hrs=5

# THIS WILL KEEP DOING SEARCHES FURTHER AND FURTHER BACK IN TIME
# USING THE MAX_ID TO THE TIMELINE 
num_tweets_collected=0
searches=[]
k=0
#KEEP SEARCHING UNTIL DESIRED NUMBER OF TWEETS COLLECTED
while num_tweets_collected<number_of_tweets or (time.time()-start_time)/60./60>max_loop_time_hrs: 
    try: 
        #FIRST SEARCH
        if len(searches)==0:
            search_results = api.search_tweets(query, lang="en", count=100)
        #ADDITIONAL SEARCHES
        else:
            search_results = api.search_tweets(query, lang="en", count=100,max_id=max_id_next)

        #UPDATE PARAMETERS
        num_tweets_collected+=len(search_results)
        max_id_next=int(search_results[-1]._json["id_str"])-1

        #SAVE SEARCH RESULTS
        searches.append(search_results)

        #SAVE TEMPORARY CHECKPOINTS (DONT DO TOO OFTEN .. SLOWS CODE DOWN)
        if(k%10==0):
            print("SEARCH-"+str(k)+" COMPLETED;  TWEETS_COLLECTED=",num_tweets_collected,"; TIME (s) = ",time.time() - start_time)
        if(k%25==0):
            save_search_tweets_results(searches,output_name="tmp-snapshot.json")
            
        k+=1
    except:
        print("WARNING: twitter search failed")

    #SLEEP 5 SECONDS BEFORE NEXT REQUEST 
    if(number_of_tweets>18000):
        time.sleep(5)
    else:
        time.sleep(0.2)
        

# REPORT BASIC SEARCH INFO
print(num_tweets_collected,len(searches))
print("search time (s) =", (time.time() - start_time)) #/60.)

#TIMESTAMP SEARCH 
now = datetime.now()
dt_string = now.strftime("%Y-%m-%Y-H%H-M%M-S%S")

#----------------------
# SAVE RESULTS
#----------------------
info_str="query = "+query+"; number_of_tweets = "+str(number_of_tweets)+"; date = "+str(dt_string)
out_name=str(dt_string)+"-twitter-search.json"
save_search_tweets_results(searches,info_str=info_str,output_name=out_name)

#CLEAN-UP TEMP FILES
os.remove("tmp-snapshot.json")
# import glob
# list_to_delete=glob.glob("./*-tmp-snapshot.json")
# for file in list_to_delete:
#     os.remove(file)