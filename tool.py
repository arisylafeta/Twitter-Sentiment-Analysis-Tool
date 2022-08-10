from textblob import TextBlob
from datetime import timedelta
import tweepy
import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
import re
import streamlit as st
import credentials
import smtplib
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime as dt



auth = tweepy.OAuthHandler(credentials.apiKey, credentials.apiKeySecret)
auth.set_access_token(credentials.accessToken, credentials.accessTokenSecret)
api = tweepy.API(auth)

tweets = pd.DataFrame()
#All function definitions 
def sendEmail(occupation, baba, msg):
   sender = "twittersent@outlook.com"
   recepient = "ari.sylafeta@gmail.com"
   smtp_server = "smtp-mail.outlook.com"
   sender_password = "strongpassword1"
   message = f"""From: From Person {sender}
                To: To Person {recepient}
                Subject: New message from TwitterSent webpage from {baba}

                I'm a {occupation} and 
                {msg}
             """

   server = smtplib.SMTP(smtp_server, 587)
   server.starttls()
   server.login(sender, sender_password)
   server.sendmail(sender, recepient, message)
   server.close()

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
   tweets = pd.read_csv("tweets.csv", index_col = 0)

def analysis(features):
   for method in features:
      if "hashtag" in method:
         hashtag()
      if "sentiment" in method:
         sentiment() 
      if "virality" in method:
         virality()

def percentage(part, whole):
   return 100* float(part)/float(whole)

def sentiment():
   tweets = pd.read_csv("tweets.csv", index_col = 0)
   tweetNum = tweets.shape[0]
   tweets.reset_index(inplace=True)
   #Perform sentiment analysis on selected tweets and adding into the respective sets
   sentiment = tweets['Text'].apply(lambda tweet: TextBlob(tweet).sentiment)
   p, s = map(list, zip(*sentiment))
   polarity = np.asarray(p)
   subjectivity = np.asarray(s)

   positive = (polarity > 0).sum()
   negative = (polarity < 0).sum()
   neutral =  (polarity == 0).sum()
   v_positive = (polarity >= 0.5).sum()
   v_negative = (polarity <= -0.5).sum()
   total = polarity.sum()
   g_sentiment = "positive" if (polarity.sum() >= 0) else "negative" 
   max_sentiment = max(polarity)
   min_sentiment = min(polarity)
    
   dates = pd.to_datetime(tweets['Date'])
   max_sdate = dates[p.index(max_sentiment)]
   min_sdate = dates[p.index(min_sentiment)]
   max_date = max(dates)
   min_date = min(dates)
   timeframe = max_date - min_date
   
   
   ############### SENTIMENT PIE CHART#################
   fig2 = go.Figure(go.Sunburst(
      labels=['Sentiment Breakdown', 'Positive', 'Negative', 'Neutral', 'Very Positive', 'Very Negative'],
      parents=['','Sentiment Breakdown','Sentiment Breakdown','Sentiment Breakdown', 'Positive', 'Negative'],
      values=[0, positive, negative, neutral, v_positive, v_negative]
   ))
   fig2.update_traces(textinfo="label+percent parent")
   fig2.update_layout(
    autosize=True,
    margin = dict(t=0, l=0, r=0, b=0))

   fig1 = go.Figure(data=go.Scatter( x=tweets['Date'], y=polarity, line= dict(color='#00CC96', width=3)))
   fig1.update_layout(
      xaxis_title='Day/Hour',
      yaxis_title='Sentiment')


   st.subheader("Let's examine the sentiment on your twitter stack")
   st.plotly_chart(fig2)

   st.write("You've collected a total of ", tweetNum, " tweets for your analysis. ", 
   positive, " tweets seem to be positive with ", v_positive, " of them being extremely positive, while "
   ,negative, " tweets seem to be negative with ", v_negative, " of them being on the extreme.") 
   st.write("The general sentiment seems to be ", g_sentiment, " with a TextBlob score of ", total, ".")
   st.write("")
   st.subheader("How did the sentiment change with time?")
   st.plotly_chart(fig1, use_container_width=True)
   st.write("The analysis has been performed on a timeframe of ", timeframe.days, " days, and ", timeframe.seconds, " seconds.")
   st.write("Sentiment seems to have increased at its maximum on ", max_sdate.strftime("%A %B %d"), "at around ", max_sdate.strftime("%H:%M"),", reaching a TextBlob sentiment score of ", max_sentiment, ".")
   st.write("On the other hand, sentiment seems to have dipped at its lowest on ", min_sdate.strftime("%A %B %d"), "at around ", min_sdate.strftime("%H:%M"), ", falling to a TextBlob sentiment score of", min_sentiment, ".")
   st.subheader("Let's take a look at these polarizing tweets")
   col1, col2 = st.columns(2)
   st.write("")
   with col1:
      st.caption("Most Positive Tweet")
      st.markdown(f'''<blockquote class="twitter-tweet"><p lang="en" dir="ltr">{tweets['Text'][p.index(max_sentiment)]}</p>&mdash; {tweets['User'][p.index(max_sentiment)]} </blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', unsafe_allow_html=True)
   with col2:
      st.caption("Most Negative Tweet")
      st.markdown(f'''<blockquote class="twitter-tweet"><p lang="en" dir="ltr">{tweets['Text'][p.index(min_sentiment)]}</p>&mdash; {tweets['User'][p.index(min_sentiment)]} </blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', unsafe_allow_html=True)

   
  
def hashtag():
   tweets = pd.read_csv("tweets.csv", index_col = 0)

   def find_hashtags(tweet):
      #This function extracts hashtags from the tweets.
      return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)
   
   tweets['hashtags'] = tweets.Text.apply(find_hashtags)
   hashtag_list = tweets['hashtags'].to_list()
   flat_hashtag = pd.DataFrame([item for sublist in hashtag_list for item in sublist])
   index = flat_hashtag.value_counts()
   tweets.reset_index(inplace=True)
   df = index.reset_index(name='count')
   fig3 = px.bar(df, x=0, y='count')
   st.subheader("Let's examine what your Twitter stack is tagging")
   st.plotly_chart(fig3)
   st.write("There is a total of ", df['count'].sum(), " hashtags within your stack with ", df.shape[0], " being distinct.")
   st.write("It seems that ", df[0][index.argmax()], " is the most mentioned hashtag amounting to ", df['count'][index.argmax()], " mentions. You can check that tweet below:")
   st.markdown(f'''<blockquote class="twitter-tweet"><p lang="en" dir="ltr">{tweets['Text'][index.argmax()]}</p>&mdash; {tweets['User'][index.argmax()]} </blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>''', unsafe_allow_html=True)
   

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
   with st.form("contact_form", clear_on_submit=True):
      st.write("Want to contact me? Complete the following")
      occupation = st.radio("What's your title?", ('Enthusiast','Recruiter'))
      email = st.text_input("Your Email")
      message = st.text_area("Write your comment", max_chars=200, height=50)
      submitted = st.form_submit_button("Submit")
      if submitted:
         sendEmail(occupation, email, message)
         st.balloons()
         st.success("Thank you for reaching out.")

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
         columns = np.array(['User', 'Text', 'Followers', 'Retweets', 'Favorites', 'Date'])
         tf = pd.read_csv(uploaded_file, )
         if tf.columns.shape == columns.shape and (tf.columns == columns).all():
            tf.to_csv('tweets.csv', index=False)
            tweets = pd.read_csv('tweets.csv')
            tweetNum = tf.shape[0]
         else:
            st.error('Your file format is not supported')
      else:
         fetchTweets(search, tweetNum, date)
      st.write("")
      if tweets.empty is False:
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
   analysis(features)




