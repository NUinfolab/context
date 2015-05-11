import re
from .bing import search as bing_search


TWITTER_LINK = re.compile('<a .*?href="http://twitter.com/(\w+)"')

def discover_twitter_users_via_bing(entity):
    r = bing_search(entity['name'])
    handles = []
    for item in r['d']['results'][0]['Web'][:10]:
        page = requests.get(item['Url']).text
        candidates = [
            s for s in list(set(TWITTER_LINK.findall(page)))
            if s != 'share']
        if len(candidates) == 1:
            if candidates[0] not in handles:
                handles.append(candidates[0])
    results = lookup_users(client, handles)
    for r in results:
        r.update({'discovered_via':'bing'})
    return results

