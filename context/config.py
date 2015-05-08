import collections
import ConfigParser
import os
import re
import sys
from os.path import expanduser

CONTEXT_CONFIG_ENV_VAR = 'CONTEXT_CONFIG'
DEFAULT_CONFIG_DIR = expanduser('~')
DEFAULT_CONFIG_FILE = 'context.cfg'
CONFIG_LIST_REGEX = re.compile(r'[, \s]+')

_config = None


def configuration():
    """Return SafeConfigParser for config file"""
    global _config
    if _config is None:
        _config = ConfigParser.SafeConfigParser()
        path = config_file_path()
        with open(path) as f:
            _config.readfp(f)
    return _config


def config_file_path():
    """Return config file path"""
    return os.getenv(CONTEXT_CONFIG_ENV_VAR,
        os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE))


def get_section_data(section='context'):
    """Return dict of config items in section"""
    config = configuration()
    d = {}
    for name, value in config.items(section):
        d[name] = value
    return d
    
    
def get_twitter_keys(section='context'):
    """Return namedtuple of Twitter config data"""
    config = configuration()
    TwitterKeys = collections.namedtuple('TwitterKeys', [
        'consumer_key',
        'consumer_secret',
        'access_token',
        'access_token_secret'])
    k = TwitterKeys(
        config.get(section, 'twitter_consumer_key'),
        config.get(section, 'twitter_consumer_secret'),
        config.get(section, 'twitter_access_token'),
        config.get(section, 'twitter_access_token_secret'))
    return k


def get_named_stoplist(name):
    """Return named stoplist."""
    config = configuration()
    stoplist = config.get('stoplists', name)
    return [s.strip() for s in CONFIG_LIST_REGEX.split(stoplist) if s.strip()]


def get_stoplist_names():
    """Return list of stoplist names"""
    config = configuration()
    return [name for name, value in config.items('stoplists')]

