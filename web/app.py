import traceback
from birdy.twitter import UserClient, TwitterAuthError, TwitterClientError
from context.config import get_twitter_keys, get_section_data
from context.query import twitter_query
from context.services.twitter import \
    search_recent, dedupe_tweets, \
    screen_name_filter, group_tweets_by_text, \
    group_tweets_by_screen_name
from context.services.reddit import search as reddit_search
from context.services.twitter import search as twitter_search
import flask
from flask import Flask, render_template, request, jsonify, url_for, redirect
from auth import get_twitter_credentials
from content import content_identifier_required, content_keywords, \
    content_entities, content_stakeholders, cached_content, content_categories
from session import session_get, session_set, \
    remove_session_credentials, session_pop, session_pop_list
from stakeholders import stakeholder_tweets
from pundits import pundit_tweets


app = Flask(__name__)


from werkzeug.wsgi import DispatcherMiddleware

app.secret_key = get_section_data()['flaskapp_secret_key']

application = DispatcherMiddleware(app, {
    '/context':     app
})


def render(data, template=None):
    if all([
        template is not None,
        'application/json' not in request.headers['Accept'],
        request.args.get('_format') != 'json'
    ]):
        return render_template(template, **data)
    else:
        return jsonify(data)


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
        token = client.get_authorize_token(callback)
        session_set(app, 'auth_token', token.oauth_token)
        session_set(app, 'auth_token_secret', token.oauth_token_secret)
        session_set(app, 'auth_redirect',
            request.args.get('redirect') or '')
        if (
                'html' in request.headers['Accept']
                and request.args.get('_format') != 'json'):
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
        session_pop_list(app,
            ['auth_token', 'auth_token_secret', 'auth_redirect'])
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

BROWSER_EXTENSIONS = [
    {   'name': 'Infolab Context Browser Extension',
        'basename': 'infolabcontext',
        'chrome': '0.1.0',
        'firefox': '0.1.0',
        'safari': '0.1.0' }
]

def browser_extensions():
    ext_url = \
        'http://23.236.61.92/context/static/browser-extensions/%s_%s.%s'
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
            'While the Firefox extension appears to be installable via direct link, it should be installed by downloading first. We are seeing different behaviors for these modes of installation, likely due to security policies in Firefox.',
            'The Chrome extension should be downloaded and copied locally into the Extensions window (Window > Extensions).',
            'The Safari exension should be downloaded, unzipped, and installed via the Extension Builder (Develop > Show Extension Builder)',
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
                return redirect(url_for('auth_check', app=app) + \
                    '?redirect=%s' % request.url)
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
        return redirect(url_for('auth_check', app=app) + \
            '?redirect=%s' % request.url)
    except TwitterClientError:
        return render({'url':request.url},
            template='twitter_client_error.jinja2')    
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e), 'url':request.url})


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
        return redirect(url_for('auth_check', app=app) + \
            '?redirect=%s' % request.url)
    except TwitterClientError:
        return render({'url':request.url},
            template='twitter_client_error.jinja2')    
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
        return redirect(url_for('auth_check', app=app) + \
            '?redirect=%s' % request.url)
    except TwitterClientError:
        return render({'url':request.url},
            template='twitter_client_error.jinja2')    
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
        return redirect(url_for('auth_check', app=app) + \
            '?redirect=%s' % request.url)
    except TwitterClientError:
        return render({'url':request.url},
            template='twitter_client_error.jinja2')    
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
