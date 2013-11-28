import tweepy
import json
import sys
import random

# Allows for multiple key sets to be used, helps with API limits
def getKeys():
    keyset1 = { "consumer_key" : '',
            "consumer_secret" : '',
            "access_token_key" : '',
            "access_token_secret" : '',
            }

    keyset2 = { "consumer_key" : '',
            "consumer_secret" : '',
            "access_token_key" : '',
            "access_token_secret" : '',
            }

    keyset3 = { "consumer_key" : '',
            "consumer_secret" : '',
            "access_token_key" : '',
            "access_token_secret" : '',
            }

    choice = random.randint(1,3)
    if choice == 1:
        keys = keyset1
    if choice == 2:
        keys = keyset2
    if choice == 3:
        keys = keyset3

    return keys

def collectTweets(API, lat, lng):
    api = API
    latitude = str(lat)
    longitude = str(lng)
    radius = str(1)
    location = latitude + "," + longitude + "," + radius + "mi"
    try:
        tweets = api.search(q='', count = 20, lang='en', result_type = 'recent', geocode = location)
    except:
        tweets = None

    return tweets

def collectUTweets(API, user):
    api = API

    user_name = str(user)
    try:
        user_tweets = api.user_timeline(screen_name = user_name, count = 5)
    except:
        user_tweets = None

    return user_tweets

def collectUsers(API, all_tweets):
    api = API
    user_name = all_tweets[0].user.screen_name
    user_tweets = api.user_timeline(screen_name = user_name, count = 5)

    for tweet in all_tweets:
        user_name = str(tweet.user.screen_name)
        try:
            user_tweets += api.user_timeline(screen_name = user_name, count = 5)
        except:
            user_tweets = None
    return user_tweets

    