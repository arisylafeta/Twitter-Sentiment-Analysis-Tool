from textblob import TextBlob
from datetime import timedelta
import asyncio
import tweepy
import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
import re
import streamlit as st
import credentials


auth = tweepy.OAuthHandler(credentials.apiKey, credentials.apiKeySecret)
auth.set_access_token(credentials.accessToken, credentials.accessTokenSecret)
api = tweepy.API(auth)

tweets = pd.read_csv("tweets.csv", index_col = 0)
#All function definitions 
def fetchTweets(keyword, num, date):
   #Fetch the tweeets based on keyword and items
   global tweets

   apiL = tweepy.Cursor(api.search_tweets,q=keyword + "-filter:retweets", lang="en", tweet_mode="extended", until=(date + timedelta(days=1))).items(num)
   #Create a list of columns and an array
   columns = ['User', 'Text', 'Followers', 'Retweets', 'Favorites', 'Date']
   data = []

   #Append tweet information to data, create a dataframe with columns and save it into a csv.
   for tweet in apiL:
      data.append([tweet.user.screen_name, tweet.full_text, tweet.user.followers_count, tweet.retweet_count, tweet.favorite_count, tweet.created_at])

   df = pd.DataFrame(data, columns=columns)
   df.to_csv('tweets.csv', index=False)

def analysis(features, tweets, tweetNum):
   for method in features:
      if "hashtag" in method:
         hashtag(tweets)
      if "sentiment" in method:
         sentiment(tweets, tweetNum) 

def percentage(part, whole):
   return 100* float(part)/float(whole)

def sentiment(tweets , tweetNum):
   #Declare variables needed for sentiment analysis
   positive = 0
   negative = 0
   neutral = 0
   polarity = 0

   #Perform sentiment analysis on selected tweets and adding into the respective sets
   sentiment = tweets['Text'].apply(lambda tweet: TextBlob(tweet).sentiment)
   for tweet in sentiment:
      polarity += tweet[0]

      if(tweet[0] == 0):
         neutral += 1
      elif(tweet[0] < 0.00):
         negative += 1
      elif(tweet[0] > 0.00):
         positive += 1
      
   #Representing the variables as a percentage of total searches
   positive = percentage(positive, tweetNum)
   negative = percentage(negative, tweetNum)
   neutral = percentage(neutral, tweetNum)
   polarity = percentage(polarity, tweetNum)

   #Fixing up the format for displaying
   positive = format(positive, '.2f')
   neutral = format(neutral, '.2f')
   negative = format(negative, '.2f')


   if(polarity == 0):
      print("Neutral")
   elif (polarity < 0.00):
      print("Negative")
   elif(polarity > 0.00):
      print("Positive")

   labels = ['Positive', 'Neutral', 'Negative']
   sizes = [positive, neutral, negative]
   explode = (0.1, 0, 0)
   colors = ['blue', 'green', 'red']
   fig1, ax1 = plt.subplots()
   ax1.pie(sizes, explode=explode, colors=colors, startangle=90, labels=labels, autopct='%1.1f%%', shadow=True)
   ax1.axis('equal')
   ax1.set_facecolor('#000000')
   st.pyplot(fig1)

def hashtag(tweets):
   
   def find_hashtags(tweet):
      #This function extracts hashtags from the tweets.
      return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)
   

   tweets['hashtags'] = tweets.Text.apply(find_hashtags)

   hashtag_list = tweets['hashtags'].to_list()
   flat_hashtag = pd.DataFrame([item for sublist in hashtag_list for item in sublist])
   st.bar_chart(flat_hashtag)
   

#Page setup and CSS
st.set_page_config(
   layout="centered",
   page_title="TwitterSent",
   page_icon="🔎")
st.markdown("""
   <style>
   .big-font {
      font-size:30px;
      font-weight: 600;
   }
   .header {
      font-size: 40px;
      font-weight: 900;
      font-family: 'Arial'
   }
   </style>
   """, unsafe_allow_html=True)

#Page sidebar
with st.sidebar:
   st.markdown('<p class="big-font">Welcome to TwitterSent 🎉 </p>', unsafe_allow_html=True)
   st.write("This platform utilizes natural language processing to extract insight from tweets. Currently the tool offers the following options")

   code = '''def TwitterSent():
         hashtag_analysis = "True"
         sentiment_analysis = "True"
         print("more to come...")'''
   st.code(code, language='python')

   st.write("")
   st.write("")
   with st.form("contact_form", clear_on_submit=False):
      st.write("Want to contact me? Complete the following")
      radio_val = st.radio("What's your title?", ('Enthusiast','Recruiter'))
      text_area = st.text_area("Write your comment", max_chars=200, height=50)

      submitted = st.form_submit_button("Submit")
      if submitted:
         st.write( "radio", radio_val)

#///////////////////////////MAIN CONTENT///////////////////////
#Logo/header
img = image.imread("logo.png")
col1, col2, col3 = st.columns([1,1,1])
col2.image(img, width=120)
st.write("")
st.write("")
st.write("")
st.write("")

#Search Fields component
st.header("1. Start out by specifying your search")
st.write("")
search = st.text_input("Enter your keyword", value="")
tweetNum = st.slider("Select the number of tweets to be searched", min_value=50, max_value=200)
date = st.date_input("Select the day you want to search from (max. 1 week)")

st.write("")
st.write("")
st.write("")

st.subheader("Alternatively you can upload a csv of your own")
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], )

st.write("")
st.write("")

#Fetch Tweets Button
if st.button("Fetch Tweets"):
   if uploaded_file is None and search == '':
       st.error('Please input a keyword or upload a file')
   else:
      if uploaded_file is not None:
         columns = ['User', 'Text', 'Followers', 'Retweets', 'Favorites', 'Date']
         tf = pd.read_csv(uploaded_file, index_col=columns)
         tf.to_csv('tweets.csv')
      else:
         fetchTweets(search, tweetNum, date)

      st.write("")
      with st.expander("Check out your data"):
         st.dataframe(tweets)
         st.write("Want to save it for later? Download it!")
         st.download_button(label="Download CSV", data=tweets.to_csv().encode('utf-8'), file_name='tweets.csv')
   


st.write("")
st.write("")
st.write("")

#Analysis Fields 
st.header("2. Select the analysis methods you want to perform")
st.write("")
features = st.multiselect("Select the analysis method", options=["hashtag analysis", "sentiment analysis"])
st.write("")
st.write("")

#Run Analysis Button
if st.button("Run Analysis"):
   analysis(features, tweets, tweetNum)




