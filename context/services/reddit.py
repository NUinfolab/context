
def search(query):
    """
    Send query to Reddit search
    """
    reddits = []   
    if query:
        headers = {'User-Agent' : 'Mozilla/5.0'}
        params = {
            'q': query,
            'limit': 10,
            'sort': 'relevance',
            't': 'month'
        }
        r = requests.get('http://www.reddit.com/search.json', params=params,
            headers=headers)
        d = r.json()
        if 'error' in d:
            if d['error'] == 429:
                raise Exception('You are being rate limited by Reddit')
            else:
                raise Exception(d['error'])       
        if 'data' in d and 'children' in d['data']:
            for r in d['data']['children']:
                reddits.append({
                    'id': r['data']['id'],
                    'title': r['data']['title'],
                    'permalink': 'http://www.reddit.com'+r['data']['permalink']
                })   
    return reddits
