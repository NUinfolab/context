import nltk
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import re
import string

_STOPWORDS = set(stopwords.words('english'))

def clean_tweet_text(tweet):
	text = tweet['text']

	# Remove any hyperlinks.
	text = re.sub(r'http[^ ]+', '', text)

	urls = tweet.get('entities', {}).get('urls', [])
	for url in urls:
		expanded_url = url.get('expanded_url')
		if expanded_url:
			text += ' ' + clean_url(expanded_url)

	return text.strip().encode('utf-8')

def clean_url(url):
	url_pat = r'(https?|ftp)://((?P<subdomain>[^.]+)\.)?'
	url_pat += r'(?P<host>[^.]+)\.(?P<domain>[^/:]+)(?P<path>[^\.]*)'
	m = re.search(url_pat, url, flags=re.I)

	is_valid = lambda x: x and x.isalnum() and not x.isdigit()
	path_tokens = filter(
		is_valid, re.split(r'[^a-z|0-9]', m.group('path'), flags=re.I))
	return '%s %s' % (m.group('host'), ' '.join(path_tokens))

def clean_text(text):
	return text.encode('utf-8')

def is_valid_bigram(bigram):
	"""
	First and second words must be capitalized and not stop words.
	"""
	return bigram[0][0].isupper() and \
		not is_stop_word(bigram[0]) and \
		bigram[1][0].isupper() and \
		not is_stop_word(bigram[1])

def is_valid_unigram(word):
	l = len(word)
	return not is_stop_word(word) and \
		word.isalnum() and \
		not word.isdigit() and \
		l > 2 and \
		l < 12

def is_stop_word(word):
	return word.lower() in _STOPWORDS

def tokenize(text, include_ngrams=True, limit_ngrams=False):
	words = wordpunct_tokenize(text)

	unigrams = filter(is_valid_unigram, words)

	bigrams = []
	if include_ngrams:
		bigrams = nltk.bigrams(words)
		if limit_ngrams:
			bigrams = filter(is_valid_bigram, bigrams)

	tokens = unigrams + map(lambda ngram: ' '.join(ngram), bigrams)

	return map(string.lower, tokens)
