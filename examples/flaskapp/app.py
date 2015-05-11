import copy
import os
import pymongo
import re
import string
import traceback
import urllib
import requests
from functools import wraps
from birdy.twitter import UserClient, TwitterAuthError
from context.config import get_twitter_keys, get_section_data, configuration
from context.nlp.classifier import classify_text
from context.content import get_article
from context.nlp.entities import get_entities, name_tokens, best_matches
from context.nlp.keywords import get_keywords
from context.nlp.util import tokenize, compare_names, name_parts
from context.query import twitter_query
from context.services import discover_twitter_users_via_bing
from context.services.twitter import \
    search_recent, dedupe_tweets, \
    screen_name_filter, group_tweets_by_text, \
    group_tweets_by_screen_name, discover_users, get_timeline
from context.services.reddit import search as reddit_search
from context.services.twitter import search as twitter_search
import flask
from flask import Flask, render_template, request, jsonify, url_for, redirect, abort
from session import session_get, session_set, \
    remove_session_credentials, session_pop, session_pop_list


ALNUM_PAT = re.compile(r'[A-Za-z0-9]+')
CONFIG_LIST_REGEX = re.compile(r'[, \s]+')

IGNORE_ENTITIES_NF = (
    ['Universiy'],
    ['God'],
    ['Catholic'],
    ['City'],
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


app = Flask(__name__)


from werkzeug.wsgi import DispatcherMiddleware

app.secret_key = get_section_data()['flaskapp_secret_key']

application = DispatcherMiddleware(app, {
    '/context':     app
})

from connection import _content, _cached_users
import bson


class InvalidRequest(Exception):
    status_code = 400


def render(data, template=None):
    if all([
        template is not None,
        'application/json' not in request.headers['Accept'],
        request.args.get('_format') != 'json'
    ]):
        return render_template(template, **data)
    else:
        return jsonify(data)


def twitter_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except TwitterAuthError:
            return url_for(auth_check)
    return wrapper


def content_identifier_required(f):
    """Enforces url query parameter on a route."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        content_id = kwargs.get('content_id')
        if content_id is None:
            content_id = request.args.get('id')
        if not 'url' in request.args and content_id is None:
            if 'application/json' not in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('url_required') + \
                    '?next=%s' % request.script_root + request.path)
            else:
                raise InvalidRequest('url parameter is required')
        if content_id:
            r = cached_content(content_id=content_id)
        else:
            url = request.args.get('url')
            if not url:
                raise InvalidRequest('URL or content ID required.')
            r = cached_content(url=url)
        if not r:
            raise Exception('Could not find article content')
        request.content = r
        return f(*args, **kwargs)
    return wrapper


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


def find_stakeholder_twitter_users(content, entities, section='context',
        credentials=None):
    """
    @entities = list of entities
    @section = config section
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
            full_results = discover_users(entity, section, credentials)
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


def stakeholder_tweets(users, keywords, section='context', credentials=None,
        limit=None):
    # Throw out users that are too ambiguous
    # TODO: ideally we would try to disambiguate and use the best option
    users = [user for user in users if len(user['twitter_users']) <= 3]
    tweets = get_timeline(users, keywords, section=section, 
        credentials=credentials, limit=limit)
    return tweets
    

def get_category_pundits(category):
    """Return list of pundits in category"""
    config = configuration()
    pundit_panel = config.get('punditpanels', category)
    return [s.strip() for s in CONFIG_LIST_REGEX.split(pundit_panel) if s.strip()]


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
        raise Exception('No pundit panel available for category "%s"' % category)    
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


@app.route('/url-required', methods=('POST', 'GET'))
def url_required():
    if request.method == 'POST':
        url = request.form['url']
        next_ = request.form['next']
        if url and next_:
            return redirect('%s?url=%s' % (next_, url))
    return render_template('url_required.jinja2', next=request.args.get('next'))


@app.route('/auth/clear/<app>')
def auth_clear(app):
    remove_session_credentials(app)
    return jsonify({ 'status': 'OK' })


@app.route('/session')
def session_show():
    return jsonify({ k:v for k,v in flask.session.iteritems() })

#
# authorization
# 

def get_twitter_credentials(app):
    access_token = session_get(app, 'access_token')
    access_token_secret = session_get(app, 'access_token_secret')
    if not (access_token and access_token_secret):     
        raise TwitterAuthError('User is not authorized')
    return {
        'access_token': access_token, 
        'access_token_secret': access_token_secret
    }


@app.route('/auth/check/<app>/')
def auth_check(app):
    """
    Check authorization.  Get signin token and auth_url, if needed.
    <app> = application identifier
    
    @redirect = redirect to this url post-authorization verification
    """
    try:
        access_token = session_get(app, 'access_token')
        access_token_secret = session_get(app, 'access_token_secret')

        if access_token and access_token_secret:        
            tk = get_twitter_keys(app)
            client = UserClient(
                tk.consumer_key,
                tk.consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret)                    
            """
            We need to make a call to verify_credentials in case the user
            has revoked access for this application. This is a rate-limited
            call and so this approach might not be ideal. If we end up
            having rate-limiting problems, we might try giving each user
            a unique application ID that is kept in local storage and used
            as a lookup for Twitter creds (vs. session data which is domain-
            specific and thus problematic for our extension-approach). This
            might allow us to consolidate Twitter creds per user rather than
            storing them for each domain visited."""
            verif = client.api.account.verify_credentials.get()
            if verif.headers['status'].split()[0] == '200':
                return jsonify({'is_auth': 1})
            else:
                # possibly revoked access, although this will probably
                # get handled by the TwitterAuthError catch
                remove_session_credentials('stakeholder')
                return jsonify({'is_auth': 0})
            
        tk = get_twitter_keys(app)
        client = UserClient(tk.consumer_key, tk.consumer_secret)

        callback = 'http://'+request.host+url_for('auth_verify', app=app)
        print 'getting auth token for callback:', callback
        token = client.get_authorize_token(callback)
                
        session_set(app, 'auth_token', token.oauth_token)
        session_set(app, 'auth_token_secret', token.oauth_token_secret)        
        session_set(app, 'auth_redirect', request.args.get('redirect') or '')
        if 'html' in request.headers['Accept'] and request.args.get('_format') != 'json':
            print 'redirecting', token.auth_url
            return redirect(token.auth_url)
        else:
            data = {'is_auth': 0, 'auth_url': token.auth_url}
            return jsonify(data)
    except TwitterAuthError:
        remove_session_credentials(app)
        return jsonify({'is_auth': 0})
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
             

@app.route('/auth/verify/<app>/')
def auth_verify(app):
    """
    Get final access token and secret, redirect   
    <app> = application identifier
    
    @oauth_verifier = parameter from auth_url callback (see above)  
    """
    try:
        oauth_verifier = request.args.get('oauth_verifier')
        if not oauth_verifier:
            raise Exception('expected oauth_verifier parameter')
        auth_token = session_get(app, 'auth_token')
        auth_token_secret = session_get(app, 'auth_token_secret')    
        auth_redirect = session_get(app, 'auth_redirect')
        if not (auth_token and auth_token_secret):
            raise Exception('Authorization credentials not found in session')
        tk = get_twitter_keys()
        client = UserClient(tk.consumer_key, tk.consumer_secret,
                    auth_token, auth_token_secret)                    
        token = client.get_access_token(oauth_verifier)
        session_set(app, 'access_token', token.oauth_token)
        session_set(app, 'access_token_secret', token.oauth_token_secret)    
        session_pop_list(app, ['auth_token', 'auth_token_secret', 'auth_redirect'])
        if auth_redirect:
            return redirect(auth_redirect)
        else:
            return redirect(url_for('home'))
    except Exception, e:
        traceback.print_exc()
        return redirect(auth_redirect)


#
# api
#

BROWSER_EXTENSIONS = (
    {   'name': 'Qwotd',
        'basename': 'qwotd',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': "Stakeholders' Tweetback",
        'basename': 'stakeholder',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'TweetTalk',
        'basename': 'tweettalk',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'Readdit',
        'basename': 'readdit',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' },
    {   'name': 'Pundits',
        'basename': 'pundits',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' }

)

def browser_extensions():
    ext_url = \
        'http://context.infolabprojects.com/static/browser-extensions/%s_%s.%s'
    return [ {
        'name': e['name'],
        'chrome': ext_url % (e['basename'], e['chrome'], 'crx'),
        'firefox': ext_url % (e['basename'], e['firefox'], 'xpi'),
        'safari': ext_url % (e['basename'], e['safari'], 'safariextension.zip'),
     } for e in BROWSER_EXTENSIONS ]


@app.route("/api")
@app.route("/")
def home():
    data = {
        'context': 'OK',
        'notes': [
            'While Firefox extensions appear to be installable via direct link, they should be installed by downloading first. We are seeing different behaviors for these modes of installation, likely due to security policies in Firefox.',
            'Chrome extensions should be downloaded and copied locally into the Extensions window (Window > Extensions).',
            'Safari exensions should be downloaded, unzipped, and installed via the Extension Builder (Develop > Show Extension Builder)',
        ],
        'resources': {
            'browser_extensions': browser_extensions()
        }
    }
    if request.url_rule.rule == '/api':
        return jsonify(data)
    else:
        return render_template('home.jinja2', **data)

  
@app.route('/url')
@app.route('/url/<app>/')
@content_identifier_required
def url_(app='qwotd'):
    """
    Search for tweets by url
    <app> = application identifier

    @url = url to search for
    """    
    try:
        url = request.args.get('url')
        if not url:
            raise Exception('Expected url parameter')
          
        try:
            credentials = get_twitter_credentials(app)
            params = {'q': url, 'count': 200}       
            tweets = search_recent(params, section=app, credentials=credentials)
        except TwitterAuthError:
            # User not authenticated. Re-initiating Twitter auth.
            if 'html' in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('auth_check', app=app)) 
            session_pop(app, 'access_token')
            session_pop(app, 'access_token_secret')
            return url_(app)
        tweets = dedupe_tweets(tweets)
        grouped = group_tweets_by_text(tweets)
        for k, tweet_list in grouped.iteritems():
            grouped[k].sort(key=lambda t: (t.retweet_count, t.created_at),
                reverse=True)
        groups = sorted(grouped.items(), key=lambda t: (-1*len(t[1]), t[0]))
        data = {'error': '', 'tweets': groups}
        return render(data, template='url.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})        


def cached_content(url=None, content_id=None):
    """Retrieve content from the cache or fetch it and cache it. Replaces
    Mongo's _id with id."""
    if url:
        r = _content.find_one({'url': url})
    elif content_id:
        r = _content.find_one({'_id': bson.ObjectId(content_id)})
    else:
        raise Exception('No Content Identifier') 
    if not r:
        data = get_article(url)
        r = {
            'url': url,
            'title': data['title'],
            'text': data['text']
        }
        _content.insert(r, manipulate=True)  # so id is set
    r['id'] = str(r['_id'])
    del r['_id']
    return r


def content_keywords(content):
    if not 'keywords' in content:
        content['keywords'] = [x for x in get_keywords(content['text'])
            if x['count'] > 2]      
        _content.save(content)
    return content['keywords']


def content_entities(content):
    if not 'entities' in content:
        content['entities'] = get_entities(content['text'])   
        _content.save(content)
    return content['entities']


def content_categories(content):
    if not 'categories' in content:
        content['categories'] = classify_text(content['text'])
        _content.save(content)
    return content['categories']


def content_stakeholders(content, app='stakeholder'):
    if not 'stakeholders' in content:
        entities = content_entities(content)
        kwargs = {
            'section': app,
            'credentials': get_twitter_credentials(app)
        }
        stakeholder_list = find_stakeholder_twitter_users(
            content['text'], entities, **kwargs)
        content['stakeholders'] = stakeholder_list
        _content.save(content)
    return content['stakeholders']


@app.route('/content/')
@content_identifier_required
def content():
    """
    Retrieve and cache content @ url
    """
    try:
        url = request.args.get('url')
        if not url:
            raise Exception('Expected url parameter')
        return render(cached_content(url=url), template='content.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})        

    
@app.route('/keywords')
@app.route('/keywords/<content_id>/')
@content_identifier_required
def keywords(content_id=None):
    """
    Retrieve and cache keywords for article with <id>.
    Automatically prune keywords with count < 2
    """
    try:
        data = content_keywords(request.content)
        return render({ 'keywords': data }, template='keywords.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
            

@app.route('/entities')
@app.route('/entities/<content_id>/')
@content_identifier_required
def entities(content_id=None):
    """
    Retrieve and cache entities for article with <content_id>. Alternatively
    accepts url or id in query params.
    """
    try:
        data = {'entities': content_entities(request.content)}
        return render(data, template='entities.jinja2')
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})

@app.route('/categories')
@app.route('/categories/<content_id>/')
@content_identifier_required
def categories(content_id=None):
    """
    Retrieve and cache categories for article with <content_id>/  Alternatively
    accepts or url or id in query params.
    """
    try:
        data = {'categories': content_categories(request.content)}
        return render(data, template='categories.jinja2')    
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
        

@app.route('/stakeholders')
@app.route('/stakeholders/<app>/<content_id>/')
@content_identifier_required
def stakeholders(app='stakeholder', content_id=None):
    """Retrieve and cache stakeholders for article with <id>
    """
    try:
        content = request.content
        data = content_stakeholders(content, app=app)
        return render({ 'stakeholders': data },
            template='stakeholders.jinja2')
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})    


@app.route('/stakeholdertweets')
@app.route('/stakeholdertweets/<app>/<content_id>/')
@content_identifier_required
def stakeholdertweets(app='stakeholder', content_id=None):
    """
    Retrieve stakeholder tweets for article with <id>
    """
    try:
        content = request.content
        keywords = content_keywords(content)
        stakeholders = content_stakeholders(content, app=app)
        stakeholders = stakeholders[:request.args.get('limit', 10)]
        credentials = get_twitter_credentials(app)
        result = stakeholder_tweets(
            stakeholders,
            keywords,
            section=app,
            credentials=credentials)
        d = group_tweets_by_screen_name([d['tweet'] for d in result])
        return render({'tweets': d.items()}, template='stakeholdertweets.jinja2')     
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
        

@app.route('/pundittweets')
@app.route('/pundittweets/<app>/<content_id>/')
@content_identifier_required
def pundittweets(app='pundits', content_id=None):
    """
    Retrieve pundit tweets for article with <id>
    """
    try:
        content = request.content
        keywords = content_keywords(content)
                  
        categories = content_categories(content)      
        if not categories:
            raise Exception('No categories found for article')    
        category = categories[0][0]
        
        credentials = get_twitter_credentials(app)
        
        tweets = pundit_tweets(
            category,
            keywords,
            section=app,
            credentials=credentials)
        tweets = dedupe_tweets(tweets)
        return render({'tweets': tweets}, template='pundittweets.jinja2')            
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})

    
@app.route('/topic')
@app.route('/topic/<app>/<content_id>/')
@content_identifier_required
def topic(app='tweettalk', content_id=None):
    """
    Search for tweets related to the topic of article with <id>
    """
    try:
        q = twitter_query(content_keywords(request.content),
            content_entities(request.content))        
        credentials = get_twitter_credentials(app)
        params = {'q': q, 'count': 100, 'result_type': 'mixed'}
        result = twitter_search(params, section=app, credentials=credentials)  
        tweets = screen_name_filter(result.statuses, 'media')
        return render( {'tweets': tweets }, template='topic.jinja2')
    except TwitterAuthError:
        # This redirect is for the HTML UI. JSON clients should execute the
        # auth-check / auth-verify cycle before making API calls
        return redirect(url_for('auth_check', app=app))
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})


@app.route('/reddits')
@app.route('/reddits/<app>/<content_id>/')
@content_identifier_required
def reddits(app='readdit', content_id=None):
    """
    Search for reddits related to the topic of article with <id>
    https://www.reddit.com/dev/api#GET_search
    
    The extension performs these functions on the client side due to 
    rate limiting, but the website needs this.
    """
    try:
        # Search by url
        reddits = reddit_search(request.content['url'])
        # Search by keyword
        keywords = content_keywords(request.content)        
        q = '+'.join(x['keyword'] for x in keywords[:3])        
        more_reddits = reddit_search(q)
        # De-dupe
        for i in xrange(len(more_reddits) - 1, -1 -1):
            id = more_reddits[i]['data']['id']
            for r in reddits:
                if id == r['id']:
                    del more_reddits[i]
        reddits.extend(more_reddits)
        return render({'reddits': reddits}, template='reddits.jinja2')    
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
                        

if __name__ == "__main__":
    app.run(debug=True)
