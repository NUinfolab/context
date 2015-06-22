import copy
import re
import string
from connection import _cached_users
from context.nlp.entities import name_tokens, best_matches
from context.nlp.util import tokenize
from context.services import discover_twitter_users_via_bing
from context.services.twitter import get_timeline, discover_users


ALNUM_PAT = re.compile(r'[A-Za-z0-9]+')
IGNORE_ENTITIES_NF = (
    ['Universiy'],
    ['God'],
    ['Catholic'],
    ['City'],
)

KNOWN_MEDIA = (
    'ac360',
    'andrewsmith810',
    'bbcnewsus',
    'bybrianbennett',
    'cnn',
    'cnnbrk',
    'glennbeck',
    'haileybranson',
    'houseonfox',
    'joejohnscnn',
    'joelrubin',
    'keyetv'
    'larrygallup',
    'latimes',
    'latvives',
    'newsweek',
    'nytimes',
    'obamainaugural',
    'reuters',
    'sam_schaefer',
    'tpm',
    'washingtonpost',
)

UNAMBIGUOUS_MEDIA_NAME_TOKENS = (
    'bbc',
    'bloomberg',
    'cnn',
    'herald',
    'nbc',
    'news',
    'nytimes',
    'reuters',
    'telegram',
    'tribune',
    'tv',
)

SKIP_TOKENS = \
    [l for l in string.ascii_lowercase] + \
    ['mr', 'mrs', 'miss', 'ms', 'dr', 'rev', 'reverend',
    'sir', 'sr', 'jr', 'mayor', 'president', 'chief', 'gov',
    'governor', 'sen', 'senator', 'sgt', 'sargeant']

def twitter_name_passes(name, entity_name_tokens):
    entity_tokens = [t.lower() for t in entity_name_tokens]
    name_tokens = [n.lower() for n in ALNUM_PAT.findall(name)]
    for token in name_tokens:
        if token in SKIP_TOKENS:
            continue
        if token not in entity_tokens:
            return False
    return True


def is_media(user):
    if user['screen_name'] in KNOWN_MEDIA:
        return True
    name_tokens = []
    description_tokens = []
    for token in tokenize(user['name']):
        for t in token.split('-'):
            name_tokens.append(t.lower())
    for token in tokenize(user['description']):
        for t in token.split('-'):
            description_tokens.append(t.lower())
    for t in UNAMBIGUOUS_MEDIA_NAME_TOKENS:
        if t in name_tokens or t in description_tokens:
            return True
    return False


def find_stakeholder_twitter_users(content, entities, credentials=None):
    """
    @entities = list of entities
    @credentials = dictionary containing token/secret overrides
    """
    users = []
    for entity in entities:
        if entity['type'] not in ('PERSON', 'ORGANIZATION'):
            continue
        if entity['name_forms'] in IGNORE_ENTITIES_NF:
            continue
        results = []
        _cached_users.ensure_index('entity')
        r = _cached_users.find_one({'entity': entity['name']})
        found_cached = False
        entity_name_tokens = name_tokens(entity)
        if r is not None:
            found_cached = True
            if r['users']:
                cached_results = [r for r in r['users'] if not is_media(r)
                    if r['verified']]
                cached_results = [r for r in cached_results if
                    twitter_name_passes(r['name'], entity_name_tokens)]
                results = cached_results
        if not found_cached:
            full_results = discover_users(entity, credentials)
            results = [r for r in full_results if r['verified']]
            results = [r for r in results if not is_media(r)]
            results = [r for r in results if
                twitter_name_passes(r['name'], entity_name_tokens)]
            if (results) == 0:
                bing_results = discover_twitter_users_via_bing(entity)
                full_results += bing_results
                bing_results = [r for r in bing_results if r['verified']]
                bing_results = [r for r in bing_results if not is_media(r)]
                bing_results = [r for r in results if
                    twitter_name_passes(r['name'], entity_name_tokens)]
                results += bing_results
            r = {
                'entity': entity['name'],
                'users': full_results
            }
            _cached_users.insert(r)
        entity_names = set([entity['name']] + entity['name_forms'])
        if len(results) > 0:
            scores = best_matches(entity_names, results)
            thresh = 0.
            scores = filter(lambda s: s[0] > thresh,scores)
            if len(scores) > 0:
                matched_users = [s[1] for s in scores]
                d = copy.copy(entity)
                d.update({ 'twitter_users':
                    [u for u in matched_users]})
                users.append(dict(d))
    return users


def stakeholder_tweets(users, keywords, credentials=None, limit=None):
    # Throw out users that are too ambiguous
    # TODO: ideally we would try to disambiguate and use the best option
    users = [user for user in users if len(user['twitter_users']) <= 3]
    tweets = get_timeline(users, keywords, 
        credentials=credentials, limit=limit)
    return tweets
    
