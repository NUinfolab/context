import newspaper
import urllib2
import requests
import bs4 as BeautifulSoup
try:
    from goose import Goose
except ImportError:
    Goose = None


def opener():
    """Return OpenerDirectory that handles HTTP Cookies"""
    return urllib2.build_opener(urllib2.HTTPCookieProcessor())


def fetch(url):
    """Return content at url using opener()"""
    return opener().open(url).read()
    

def extract_with_goose(html):
    """Extract content with Goose"""
    a = Goose().extract(raw_html=html)
    return {
        'html': html,
        'title': a.title,
        'text': a.cleaned_text
    }


def fetch_extract_with_newspaper(url):
    """Extract content with newspaper"""
    a = newspaper.Article(url)
    a.download()
    a.parse()
    return {
        'url': url,
        'html': a.html,
        'title': a.title,
        'text': a.text
    }


def get_article(url):       
    """Return article at url""" 
    newspaper_article = fetch_extract_with_newspaper(url)
    if newspaper_article['text']:
        return newspaper_article
    article = { 'url': url }
    if newspaper_article['html']:
        article['html'] = newspaper_article['html']
    else:
        article['html'] = fetch(url)
    if Goose is not None:
        goose = extract_with_goose(article['html'])
        article['title'] = goose['title']
        article['text'] = goose['text']
    else:
        article['title'] = ''
        article['text'] = ''
    return article


def all_page_text(url):
    try:
        html = requests.get(url).text
        doc = BeautifulSoup.BeautifulSoup(html)
        return ' '.join([t for t in doc.findAll(text=True) if t.strip()])
    except requests.ConnectionError:
        return ''

