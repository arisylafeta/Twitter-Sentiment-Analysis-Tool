from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
import re
import streamlit as st


class myCredentials:
  apiKey = "WAnzVHUJZLwBrWxlCpSo86CK0"
  apiKeySecret = "d0s4JnADB2HY2xycj7JlJQKc4UAGdLZZMnaM9cuBvWU9XkBu3c"
  accessToken = "1455457811186454530-dI3GomJvxFMLzKiMXMwLSsPAp2sUAn"
  accessTokenSecret = "VueS6hQ7FBGqcZ3WJKSUmdpjeQMe4gVpoocitTnLeccxD"

credentials = myCredentials()

#Linking with our Twitter API, If connection fails, check that you've filled credentials in credentials.py and read the README.txt file
auth = tweepy.OAuthHandler(credentials.apiKey, credentials.apiKeySecret)
auth.set_access_token(credentials.accessToken, credentials.accessTokenSecret)
api = tweepy.API(auth)

def run(keyword, num, list):
   #Fetch the tweeets based on keyword and items
   tweets = tweepy.Cursor(api.search_tweets,q=keyword + "-filter:retweets", lang="en", tweet_mode="extended").items(num)
   #Create a list of columns and an array
   columns = ['User', 'Text', 'Followers', 'Retweets', 'Favorites', 'Date']
   data = []

   #Append tweet information to data, create a dataframe with columns and save it into a csv.
   for tweet in tweets:
      data.append([tweet.user.screen_name, tweet.full_text, tweet.user.followers_count, tweet.retweet_count, tweet.favorite_count, tweet.created_at])

   df = pd.DataFrame(data, columns=columns)
   """df.to_csv('tweets.csv', index = False)

   # read formatted info from csv and assing it to tweets
   tweets = pd.read_csv("tweets.csv", index_col = 0)


st.set_page_config(
   layout="centered",
   page_title="TwitterSent",
   page_icon="🔎"
)
img = image.imread("logo.png")

st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: 600;
}
.header {
   font-size: 40px;
   font-weight: 900;
   font-family: 'Arial'
}
</style>
""", unsafe_allow_html=True)


col1, col2, col3 = st.columns([1,1,1])
col2.image(img, width=120)
st.write("")
st.write("")
st.write("")
st.write("")
st.markdown('<p class="big-font">Start out by searching a keyword </p>', unsafe_allow_html=True)

search = st.text_input("Enter your keyword")
tweetNum = st.slider("Select the number of tweets to be searched", min_value=50, max_value=200)
features = st.multiselect("Select the analysis types you want to conduct", options=["hashtag analysis", "sentiment analysis"])
st.button("Submit", on_click=run(search, tweetNum, features))



st.sidebar.markdown('<p class="big-font">Welcome to TwitterSent 🎉 </p>', unsafe_allow_html=True)
st.sidebar.write("This platform utilizes natural language processing to extract insight from tweets. Currently the tool offers the following options")

code = '''def TwitterSent():
      hashtag_analysis = "True"
      sentiment_analysis = "True"
      print("more to come...")'''
st.sidebar.code(code, language='python')

with st.sidebar.form("contact_form", clear_on_submit=False):
   st.write("Want to contact me? Complete the following")
   radio_val = st.radio("What's your title?", ('Enthusiast','Recruiter'))
   text_area = st.text_area("Write your comment", max_chars=200, height=50)

   submitted = st.form_submit_button("Submit")
   if submitted:
        st.write( "radio", radio_val)



#Creating a percentage function that will be useful when doing the sentiment analysis
def percentage(part, whole):
   return 100* float(part)/float(whole)

def sentiment(tweets):
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

def hashtag(tweets):
   
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






