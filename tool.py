import sys, os
sys.path.append(os.path.join(os.path.dirname('\\scb-sv-fs-1\users$\as2238\Desktop\TwitterBot'), '..'))

from tweepy.streaming import Streamlistener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials



auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)