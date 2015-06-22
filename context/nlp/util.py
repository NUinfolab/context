import nltk
import re

_stemmer = None
_lemmatizer = None

def nltk_major_version():
    return int(nltk.__version__.split('.')[0])
    
NLTK_VERSION = nltk_major_version()
ALNUM_PAT = re.compile(r'[A-Za-z0-9]+')
MULTIWORD_PAT = re.compile(r'(.*) +(.*)')
   

def get_sentences(text):
    """Return sentence list"""
    if text.strip() == '':
        return []
    tokens = nltk.sent_tokenize(text)
    sentences = []
    for sent in tokens:
        sentences.extend([s.strip() for s in sent.split('\n') if s.strip()])
    sentences_ = []
    skip_next = False
    for i, sent in enumerate(sentences):
        if skip_next:
            skip_next = False
            continue
        if i == len(sentences):
            sentences_.append(sent)
            break
        if sent.split()[-1].lower() == ('no.'):
            try:
                s1 = sentences[i+1]
                int(s1.split()[0])
                sentences_.append(sent + ' ' + s1)
                skip_next = True
            except ValueError:
                sentences_.append(sent)
        else:
            sentences_.append(sent)
    assert sentences[-1] in sentences_[-1]
    return sentences_


def pos_tag(tokens):
    """Return POS tagged tokens"""
    return nltk.pos_tag(tokens)


def tokenize(text):
    """Return tokenized string"""
    text = text.replace('@', '__at__')
    tokens = nltk.word_tokenize(text)
    tokens = [t.replace('__at__', '@') for t in tokens]
    return tokens


def stem(word):
    """Return stemmed word using PorterStemmer"""
    global _stemmer
    if _stemmer is None:
        _stemmer = nltk.stem.porter.PorterStemmer()
    return _stemmer.stem_word(word)


def lemmatize(word):
    """Return lemmatized word using WordNetLemmatizer"""
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = nltk.WordNetLemmatizer()
    return _lemmatizer.lemmatize(word) 


def normalize(word):
    """Return lowercased, stemmed, and lemmatized word."""
    return lemmatize(stem(word.lower()))


def compare_names(namepartsA, namepartsB):
    """Takes two name-parts lists (as lists of words) and returns a score."""
    complement = set(namepartsA) ^ set(namepartsB)
    intersection = set(namepartsA) & set(namepartsB)
    score = float(len(intersection))/(len(intersection)+len(complement))
    return score


def name_parts(names, flat=False):
    """Return list of words within a name"""
    parts = []
    for name in names:
        n = ALNUM_PAT.findall(name)
        if flat:
            parts.extend(n)
        else:
            parts.append(n)
    return parts


def quoted_terms(term_list):
    """Return list of terms with multi-word terms quoted"""
    return [MULTIWORD_PAT.sub(r'"\1 \2"', t) for t in term_list]
