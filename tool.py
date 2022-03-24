import tweepy
import pandas as pd
import credentials

auth = tweepy.OAuthHandler(credentials.apiKey, credentials.apiKeySecret)
auth.set_access_token(credentials.accessToken, credentials.accessTokenSecret)
api = tweepy.API(auth)
keyword = 'Bitcoin'
date_since = '2022-03-20'
cursor = tweepy.Cursor(api.search_tweets, q= 'Bitcoin', tweet_mode="extended").items(1)

for i in cursor:
   print(i.full_text)