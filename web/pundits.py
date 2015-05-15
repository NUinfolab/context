import re
from context.config import configuration
from context.query import twitter_query
from context.config import get_twitter_keys
from context.services.twitter import search as twitter_search
from birdy.twitter import UserClient

CONFIG_LIST_REGEX = re.compile(r'[, \s]+')


def get_category_pundits(category):
    """Return list of pundits in category"""
    config = configuration()
    pundit_panel = config.get('punditpanels', category)
    return [s.strip() for s in
        CONFIG_LIST_REGEX.split(pundit_panel) if s.strip()]


def get_pundit_categories():
    """Return list of pundit categories"""
    config = configuration()
    return [category for category, value in config.items('punditpanels')]


def chunk_iter(seq, n):
    """
    Break seq into chunks of at most n items
    """
    return (seq[pos:pos + n] for pos in xrange(0, len(seq), n))


def pundit_tweets(category, keywords, section='context', credentials=None, 
    limit=None):
    """
    Do keyword search of tweets from pundits in category
    Twitter says to keep keywords and operators < 10
    """
    categories = get_pundit_categories()
    if not category in categories:
        raise Exception(
            'No pundit panel available for category "%s"' % category)    
    pundits = get_category_pundits(category)
    if not pundits:
        raise Exception('No pundits available for category "%s"' % category)
    n_keywords = 4
    while True:
        q_keywords = twitter_query(keywords[:n_keywords])
        n_from = (10 - len(q_keywords.split())) / 2      
        if n_from > 0:
            break
        n_keywords -= 1
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    tweets = []    
    for group in chunk_iter(pundits, n_from):    
        q_from = ' OR '.join(['from:%s' % x for x in group])
        q = '(%s) AND (%s)' % (q_from, q_keywords)
        params = {'q': q, 'count': 20, 'result_type': 'mixed'}
        result = twitter_search(
            params, section=section, credentials=credentials)
        if len(result.statuses) != 0:
            tweets.extend(result.statuses)
    return tweets

