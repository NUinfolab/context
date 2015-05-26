import os
import json


VERSION = '1.7.6'
BUILD = 'e5b39c50d196'
PACKAGE_ID = 'dev'

KEYWORDS = {
    "product": "kango",
    "ie.engine": "KangoEngine",
    "ie.bho": "KangoBHO"
}

try:
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.json'), 'r') as f:
        settings = json.load(f)
        KEYWORDS.update(settings.get('keywords', {}))
except IOError:
    pass