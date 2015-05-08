# -*- coding: utf-8 -*-
import copy
import os
import re
import urllib
import requests
import string
from collections import defaultdict, OrderedDict
import birdy.twitter
from ..config import get_twitter_keys, get_named_stoplist
from ..content import all_page_text
from ..nlp.keywords import check_keywords
from ..nlp.entities import collapse_entities
from ..nlp.util import tokenize, compare_names, name_parts, ALNUM_PAT
from nltk import ngrams
from nltk.corpus import stopwords

URL_PAT = re.compile(r'http[^ ]+', re.I)
USER_PAT = re.compile(r'@\w{1,15}')    

LEAD_PAT = re.compile(u'^(RT)?\s*[.?!:;,\'"‘’“”—…\s]*', re.U | re.I)     
TRAIL_PAT = re.compile(u'[\s.:—…]+$', re.U)


class UserClient(birdy.twitter.UserClient):
    """Twitter UserClient"""
    def __repr__(self):
        return dict(self).__repr__


_client = None
def client():
    """Get Twitter UserClient"""
    global _client
    if _client is None:
        _client = UserClient(*get_twitter_keys())
    return _client


def best_users(entity_names, twitter_objs):
    twitter_name_parts = name_parts([obj['name'] for obj in twitter_objs])
    entity_name_parts = name_parts(entity_names, flat=True)
    matches = map(lambda x: compare_names(entity_name_parts, x),
        twitter_name_parts)
    return sorted(zip(matches, twitter_objs), reverse=True)


def dedupe_tweets(tweet_list):
    """
    Return de-duped list of tweets by throwing out retweets.  Assumes
    list of tweets is in reverse chronological order.
    """
    tweets = []
    id_set = set()
    
    tweet_list.sort(key=lambda x: x['created_at'])
    for tweet in tweet_list:
        if tweet.id_str in id_set:
            continue
        id_set.add(tweet.id_str)
   
        try:
            rt_id_str = tweet.retweeted_status.id_str
            if rt_id_str in id_set:
                continue
            id_set.add(rt_id_str)
        except AttributeError:
            pass
                                            
        tweets.append(tweet)
    
    return list(reversed(tweets))    


def group_tweets_by_screen_name(tweet_list):
    """Return dict of tweet lists grouped by user screen_name"""
    d = OrderedDict()
    for tweet in tweet_list:
        screen_name = '@'+tweet.user.screen_name
        if screen_name in d:
            d[screen_name].append(tweet)
        else:
            d[screen_name] = [tweet]
    return d
            

def group_tweets_by_text(tweet_list):
    """
    Return dict of tweet lists grouped by text, merging superstring
    groups into substring group.
    """
    d = defaultdict(list)    
    for tweet in tweet_list:
        s = USER_PAT.sub('', URL_PAT.sub(' ', tweet.text))
        s = LEAD_PAT.sub('', TRAIL_PAT.sub('', s))
        if s:
            d[s].append(tweet)  
    
    results = defaultdict(list)
    k = sorted(d.keys(), key=lambda k: len(k))
        
    while k:
        key = k.pop(0)
        results[key].extend(d[key])

        # Try to deal with in-line hashtags and trivial whitespace
        pat = '\s+'.join(
            ['#?'+x[1:] if x[0] == '#' else '#?'+x for x in key.split()])
        try:
            regex = re.compile(pat, re.I)
            for i in range(len(k) - 1, -1, -1):
                s = k[i]
                if regex.search(s):
                    results[key].extend(d[s])               
                    del k[i]       
        except Exception, e:
            pass
                                                      
    return results


def search(params, section='context', credentials=None):
    """
    Execute twitter search
    
    @params = dictionary of search parameters
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    return client.api.search.tweets.get(**params).data


def search_recent(params, section='context', credentials=None):
    """
    Execute twitter search for most_recent tweets (allows pagination)
    @return list of tweets in reverse chronological order
   
    @params = dictionary of search parameters
    @section = config section
    @credentials = dictionary containing token/secret overrides
    """
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)
    tweets = []
    params['result_type'] = 'recent'
    n_tweets = 0
    n_max = params['count']    
    while n_tweets < n_max:
        params['count'] = min(100, n_max - n_tweets)        
        data = client.api.search.tweets.get(**params).data
        n = len(data.statuses)          
        if not n:
            break
        tweets.extend(data.statuses)
        n_tweets += n
        params['max_id'] = (int(data.statuses[-1].id_str) - 1)
    return tweets     


def lookup_users(client, handles):
    if not handles:
        return []
    try:
        return client.api.users.lookup.post(
            screen_name=','.join(handles)).data
    except birdy.twitter.TwitterApiError, e:
        raise e
        if str(e).startswith('Invalid API resource.'):
            return lookup_users(client, handles[:-1])
        else:
            raise e


def get_timeline(users, keywords, section='context', credentials=None, limit=None):
    tk = get_twitter_keys(section)._replace(**credentials or {})        
    client = UserClient(*tk)

    tweets = []
    closed = []
    for i, user in enumerate(users):
        if limit is not None and i >= limit:
            break
        for user in user['twitter_users']:
            if user['id'] not in closed:
                timeline = client.api.statuses.user_timeline.get(
                    count=200, user_id=user['id']).data
                if timeline is not None:
                    closed.append(user['id'])
                    twits = check_keywords(timeline, keywords)
                    if len(twits) != 0:
                        tweets.extend(twits)
    return tweets


def screen_name_filter(tweet_list, stoplist):
    """
    Filter list of tweets by screen_names in stoplist.
    Pulls original tweets out of retweets.

    stoplist may be a list of usernames, or a string name of a configured
    named stoplist.
    """
    tweets = []
    id_set = set()
    if isinstance(stoplist, basestring):
        stoplist = get_named_stoplist(stoplist)
    stoplist = [n.lower() for n in stoplist]
    for tweet in tweet_list:
        if tweet.id_str in id_set:
            continue
        id_set.add(tweet.id_str)
        if tweet.user.screen_name.lower() in stoplist:
            continue
        try:
            rs = tweet.retweeted_status
            if rs.id_str in id_set:
                continue
            id_set.add(rs.id_str)
            if rs.user.screen_name.lower() in stoplist:
                continue
            tweets.append(tweet.rs)
        except AttributeError:
            tweets.append(tweet)
    return tweets
