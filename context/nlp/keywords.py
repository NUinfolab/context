"""
Partly based on this gist: https://gist.github.com/alexbowe/879414
"""
import nltk
from nltk.corpus import stopwords
from operator import itemgetter
from util import get_sentences, tokenize, pos_tag, normalize, NLTK_VERSION

STOPWORDS = stopwords.words('english')


#Taken from Su Nam Kim Paper...
KEYWORD_GRAMMAR = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""

_keyword_chunker = None
def chunk(tokens):
    global _keyword_chunker
    if _keyword_chunker is None:
        _keyword_chunker = nltk.RegexpParser(KEYWORD_GRAMMAR)
    return _keyword_chunker.parse(tokens)


def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    if NLTK_VERSION >= 3:
        filter_ = lambda t: t.label()=='NP'
    else:
        filter_ = lambda t: t.node == 'NP'
    for subtree in tree.subtrees(filter=filter_):
        yield subtree.leaves()


def get_terms(tree):
    for leaf in leaves(tree):
        term = [w for w,t in leaf]
        if term[0].lower() in STOPWORDS or term[-1].lower() in STOPWORDS:
            continue
        yield term


def _keywords(term, location, data):
    key = tuple([normalize(w) for w in term])
    if not key in data:
        data[key] = {
            'count': 0,
            'term_forms': [],
            'locations': []
        }
    data[key]['count'] += 1
    term_form = ' '.join([w for w in term])
    if term_form not in data[key]['term_forms']:
        data[key]['term_forms'].append(term_form)
    data[key]['locations'].append(location)
    return


def get_keywords(text):
    data = {}
    for i, sentence in enumerate(get_sentences(text), start=1):
        tagged_tokens = pos_tag(tokenize(sentence))
        for term in get_terms(chunk(tagged_tokens)):
            _keywords(term, i, data)
    keywords = [{
        'keyword': v['term_forms'][0],
        'count': v['count'],
        'locations': v['locations']
    } for k, v in data.items()]
    return sorted(keywords, key=itemgetter('count'), reverse=True)


def check_keywords(timeline, keywords):
    tweets = []
    keywords = [k['keyword'] for k in keywords]
    for tweet in timeline:
        score = 0
        for kw in keywords:
            if kw.lower() in tweet.text.lower():
                score += 1
        if score > 0:
            tweets.append({
                'tweet': tweet,
                'score': score})
    tweets = sorted(tweets, key = lambda x: x['score'], reverse=True)
    return tweets
