# -*- coding: utf-8 -*-
import urllib
import requests
from ..config import configuration

config = configuration()
BING_ACCOUNT = config.get('context', 'bing_account')
BING_SEARCH_ACCOUNT_KEY = config.get('context', 'bing_search_account_key')

BING_URL = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%%27web%%27&$format=json&Query=%s'


def search(query):
    query = "'%s'" % query
    req = BING_URL % urllib.quote(query)
    if len(req) > 2047:
        raise Exception
    r = requests.get(req, auth=(BING_ACCOUNT, BING_SEARCH_ACCOUNT_KEY))
    return r.json()

