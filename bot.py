import tweepy
import logging
from config import create_api
import time
from textblob import TextBlob 
import re
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def response(sentiment):

    logger.info("Replying for sentiment %s - " % (sentiment))

    responses = {
        "positive": [
            "Are you feeling good?",
            "Such a happy day!",
            "I feel you are pleased about this!"
        ],
        "neutral": [
            "I understand.",
            "I totally get it.",
            "Yeah, it is so."
        ],
        "negative": [
            "Oh no, that is bad!",
            "Oops, sorry that it is so!",
            "That is really sad."
        ]
    }

    return responses[sentiment][random.randint(0, 2)]

def clean_tweet(tweet): 
    logger.info("Cleaning tweet")
    tweet = tweet.replace(" sentix", "")
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

def get_tweet_sentiment(tweet): 
    logger.info("Determining tweet sentiment")
    analysis = TextBlob(clean_tweet(tweet)) 
    if analysis.sentiment.polarity > 0: 
        logger.info("Sentiment: Positive")
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        logger.info("Sentiment: Neutral")
        return 'neutral'
    else: 
        logger.info("Sentiment: Negative")
        return 'negative'

def check_mentions(api, keywords, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    cursor = tweepy.Cursor(api.mentions_timeline, since_id=since_id)

    mentions = []

    for tweet in cursor.items():
        mentions.insert(0, tweet)
    
    for tweet in mentions:
        new_since_id = max(tweet.id, new_since_id)
        logger.info("New since id: %d - " % (new_since_id))
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            logger.info(f"Answering to {tweet.user.screen_name} at {tweet.id}")

            sentiment = get_tweet_sentiment(tweet.text)

            api.update_status(
                status="Hey @%s, %s" % (tweet.user.screen_name, response(sentiment)),
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True
            )

    return new_since_id

def main():
    api = create_api()
    last_tweet = api.user_timeline(count=1)
    since_id = last_tweet[0].id

    logger.info("Starting with id: %d - " % (since_id))

    while True:
        since_id = check_mentions(api, ["sentix"], since_id)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()