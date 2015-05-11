import sys
from context.config import get_named_stoplist
from context.content import get_article
from context.nlp.keywords import get_keywords
from context.nlp.entities import get_entities
from context.services.twitter import search, screen_name_filter
from context.query import twitter_query


def topictweets(url):
    """Find tweets by topic"""
    article = get_article(url)
    keywords = get_keywords(article['text'])
    entities = get_entities(article['text'])
    q = twitter_query(keywords, entities)
    result = search({'q': q, 'count': 100, 'result_type': 'mixed'})
    tweets = screen_name_filter(result.statuses, 'media')
    return tweets


if __name__=='__main__':
    url = sys.argv[1]
    tweets = topictweets(url)
    for tweet in tweets:
        print '@'+tweet.user.screen_name, tweet.text
