from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import credentials
import re

#Creating a percentage function that will be useful when doing the sentiment analysis
def percentage(part, whole):
   return 100* float(part)/float(whole)

#Linking with our Twitter API, If connection fails, check that you've filled credentials in credentials.py and read the README.txt file
auth = tweepy.OAuthHandler(credentials.apiKey, credentials.apiKeySecret)
auth.set_access_token(credentials.accessToken, credentials.accessTokenSecret)
api = tweepy.API(auth)

#Prompting user for their searchterm and how sample size
keyword = input("Enter keyword/hashtag to search about: ")
noOfSearchTerm = int(input("Enter how many tweets to analyze: "))

#Fetch the tweeets based on keyword and items
tweets = tweepy.Cursor(api.search_tweets,q= keyword + "-filter:retweets", lang="en", tweet_mode="extended").items(noOfSearchTerm)

#Declare variables needed for sentiment analysis
positive = 0
negative = 0
neutral = 0
polarity = 0


#Perform sentiment analysis on selected tweets and adding into the respective sets
for tweet in tweets:
   analysis = TextBlob(tweet.full_text)
   polarity += analysis.sentiment.polarity

   if(analysis.sentiment.polarity == 0):
      neutral += 1
   elif(analysis.sentiment.polarity < 0.00):
      negative += 1
   elif (analysis.sentiment.polarity > 0.00):
      positive += 1
      
#Representing the variables as a percentage of total searches
positive = percentage(positive, noOfSearchTerm)
negative = percentage(negative, noOfSearchTerm)
neutral = percentage(neutral, noOfSearchTerm)
polarity = percentage(polarity, noOfSearchTerm)

#Fixing up the format for displaying
positive = format(positive, '.2f')
neutral = format(neutral, '.2f')
negative = format(negative, '.2f')


print("How people are reacting on" + keyword + " by analyzing " + str(noOfSearchTerm) + " Tweets.")

if(polarity == 0):
   print("Neutral")
elif (polarity < 0.00):
   print("Negative")
elif(polarity > 0.00):
   print("Positive")

labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]', 'Negative [' + str(negative) + '%]']
sizes = [positive, neutral, negative]
colors = ['yellowgreen', 'gold', 'red']
patches, texts = plt.pie(sizes, colors=colors, startangle=90)
plt.legend(patches, labels, loc="best")
plt.title('How people are reacting on ' + keyword + 'by analyzing ' + str(noOfSearchTerm) + ' Tweets.')
plt.axis('equal')
plt.tight_layout()
plt.show()

"""
#Create a list of columns and an array
columns = ['User', 'Text', 'Followers', 'Retweets', 'Favorites', 'Date']
data = []

#Append tweet information to data, create a dataframe with columns and save it into a csv.
for tweet in tweets:
   data.append([tweet.user.screen_name, tweet.full_text, tweet.user.followers_count, tweet.retweet_count, tweet.favorite_count, tweet.created_at])

df = pd.DataFrame(data, columns=columns)
df.to_csv('tweets.csv', index = False)

# read formatted info from csv and assing it to tweets
tweets = pd.read_csv("tweets.csv", index_col = 0)


def find_hashtags(tweet):
    #This function extracts hashtags from the tweets.
    return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)
  

tweets['hashtags'] = tweets.Text.apply(find_hashtags)

hashtag_list = tweets['hashtags'].to_list()
flat_hashtag = pd.DataFrame([item for sublist in hashtag_list for item in sublist])
flat_hashtag.shape

flat_hashtag.columns = ['hashtags']
flat_hashtag.head()
flat_hashtag['hashtags'].value_counts()[:20].plot(kind='barh')
plt.show()

#define a function to clean up the tweets. input - text field of all #the rows, output - cleaned text 
def cleanUpTweet(txt):
    # Remove mentions
    txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
    # Remove hashtags
    txt = re.sub(r'#[A-Z0-9]+', '', txt)
    # Remove retweets:
    txt = re.sub(r'RT : ', '', txt)
    # Remove urls
    txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
    #remove amp
    txt = re.sub(r'&amp;', '', txt)
    #rempve strange characters
    txt = re.sub(r'ðŸ™', '', txt)
    #remove new lines
    txt = re.sub(r'\n', ' ', txt)
    return txt
tweets['Cleaned_Text'] = tweets['Text'].apply(cleanUpTweet)
"""