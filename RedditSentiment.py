"""Author: Ethan Jones
Assingment: EE551 Final
Date: 12/17/2020
"""
#! python3
import praw #is the reddit api wrapper which makes data calls easier
import pandas as pd  #needed to work with data
import argparse    	 # for parsing the arguments in the command line
import datetime as dt #needed to convert datetime
import csv #needed to read in csv file
from IPython.core.display import display, HTML #for displaying to jupyter
from urllib.parse import urlparse #for parsing url to find news source
import re # used for regex split of strings
from textblob import TextBlob # needed to calculate the polarity and subjectivity
#Ethan Jones        EE551 Final
#I pledge my honor that I have abided by the stevens honor code
#
#polarity = positivity(+1) or rnegativity(-1) of a piece of text
#subjectivity = subjectivity(0.0) or objectivity(+1) of a piece of text
#
#When used in conjunction with jupyter, this program will provide visual charts
#which expand on the differences among the political subreddits and how they
#they reacted to different submissions

# to run from terminal window:
#        python  RedditSentiment.py   --search_term  mysearch --search_term2 mysearch2 --submission_max  mymaxsubmissions --comment_max mymaxcomments
# where:  mysearch is the term the user wants to search for;  default = conservative
# where:  mysearch2 is the second term the user wants to search for: default = politics
# where:  mymaxsubmissions is the maximum number of submissions;  default = 10
#   and:  mymaxcomments is the maximum number of comments;  default = 5


parser = argparse.ArgumentParser(description='Political Subreddit Search')
parser.add_argument("--search_term", action='store', dest='search_term', default="conservative")
parser.add_argument("--search_term2", action='store', dest='search_term2', default="politics")
parser.add_argument("--submission_max", action='store', dest='submission_max', default=10)
parser.add_argument("--comment_max", action='store', dest='comment_max', default=5)
args = parser.parse_args()

search_term = args.search_term
search_term2= args.search_term2
submission_max = int(args.submission_max)
comment_max = int(args.comment_max)

bias_dict =  { "news_source":[], \
                "rating":[], \
                "rating_num": [], \
                "type": [], \
                "perc_agree":[]}
 #dictionary to represent the entries
 #on the news organizations biases by allSides


with open('allsides.csv') as csv_file:          #reads in the csv file of the
    csv_reader = csv.reader(csv_file, delimiter = ',')  #entries on biases
    line_count = 0                      #among news organizations
    for row in csv_reader:
        if line_count == 0:             #skips the first line for the headers
            print("loading bias csv")
            line_count+=1
        else:
            bias_dict["news_source"].append(row[0].replace(" ","").lower())
            bias_dict["rating"].append(row[1])
            bias_dict["rating_num"].append(row[2])
            bias_dict["type"].append(row[3])
            bias_dict["perc_agree"].append(row[4])
            line_count+=1

bias_data = pd.DataFrame(bias_dict)     #creates a data frame which can be represented
                                        #beautifully in jupyter

reddit = praw.Reddit(client_id='WmdfO7LRyqE0Hg', \
                     client_secret='99OtNMwKpzbxmV-FJ-Y8GiEa6cUOJw', \
                     user_agent='Political Sentiment identifier(EE551 FINAL)', \
                     username='EE551-API-Test', \
                     password='OgsIsAtTheWheel20')
#creating a reddit instance with praw

def subreddit_chart(subred):
    subred_dict = { "title":[], \
                    "score":[], \
                    "id":[], "url":[], \
                    "created": [], \
                    "body":[], \
                    "comment_polarity":[], \
                    "comment_subjectivity":[], \
                    "news_source":[]}
                    #dictionary to represent the different
                    #submissions in a subreddit

    subreddit = reddit.subreddit(subred)        #creating an instance of the subreddit that is passed

    subreddit_polarity = 0.0                #initializing the polarity and subjectivity values
    subreddit_subjectivity = 0.0

    top_subreddit = subreddit.top(limit=submission_max)    #finds the top 10 submissions on the subreddit
    for submission in top_subreddit:
        subred_dict["title"].append(submission.title)
        subred_dict["score"].append(submission.score)
        subred_dict["id"].append(submission.id)
        subred_dict["url"].append(submission.url)
        subred_dict["created"].append(submission.created)
        body = submission.selftext             #limit the text in a submission body
        if len(body) > 125:                    #to 125 characters as some bodies were
            body = body[0:125]                 #thousands of words long
        subred_dict["body"].append(body)

        source = urlparse(submission.url).netloc    #parse the url and keep the domain
        source = source.replace("www.","")          #remove wwww.
        source = source.split(".")[0]               #remove every extension extension
        source = re.split('\d+',source)[0]          #remove any digits and any characters after
        subred_dict["news_source"].append(source)

        submission_polarity = 0.0                   #initializing the submission
        submission_subjectivity = 0.0               #polarity and subjectivityS

        for x in range(comment_max):                                       #iterates through the top 5 comments of the submission
            text_blob = TextBlob(submission.comments[x].body)    #sets up each comment with textblob
            submission_polarity += text_blob.polarity            #calculates comments polarity and adds it to the sub total
            submission_subjectivity += text_blob.subjectivity    #calculates comments subjectivity and adds it to the sub total

        subreddit_polarity += submission_polarity
        subreddit_subjectivity += submission_subjectivity

        subred_dict["comment_polarity"].append(submission_polarity)
        subred_dict["comment_subjectivity"].append(submission_subjectivity)

    subreddit_data = pd.DataFrame(subred_dict)              #setting up the subreddit data frame to be displayed
    def get_date(created):                                  #fixing the created timestamp
        return dt.datetime.fromtimestamp(created)           #since reddit using a specific data type which isn't

    _timestamp = subreddit_data["created"].apply(get_date)  #understandable
    subreddit_data = subreddit_data.assign(timestamp = _timestamp)
    display(HTML(' <span style="color:red"><h1>'+ "r/" + subred + '</h1> </span>  '))   #print html to show the subreddit, polarity and subjectivity
    display(HTML(' <span style="color:black"> <h3>'+ "Polarity: " + str(subreddit_polarity) + '</h3> </span>  '))
    display(HTML(' <span style="color:black"> <h3>'+ "Subjectivity: " + str(subreddit_subjectivity) + '</h3> </span>  '))

    display(HTML(subreddit_data.to_html()))         #display the charts through jupyter

    return subreddit_data       #returns the data frame in case it is needed later on





subreddit_chart(search_term)        #call the function to show the charts for the search terms
subreddit_chart(search_term2)

display(HTML(bias_data.to_html()))  #display the bias chart derived from the csv file
