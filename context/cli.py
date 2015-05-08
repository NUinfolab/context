import click
import pprint
from .config import config_file_path, get_stoplist_names
from .content import get_article
from .entities import extract_entities
from .keywords import get_keywords
from .classifier import classify_text

pp = pprint.PrettyPrinter()


@click.group()
def cli():
    """Context CLI application"""
    pass


@click.command()
@click.argument('url')
def content(url):
    """Extract primary article content"""
    pp.pprint(get_article(url))


@click.command()
@click.argument('url')
def entities(url):
    """Extract named entities"""
    pp.pprint(extract_entities(get_article(url)['text']))


@click.command()
@click.argument('url')
def keywords(url):
    """Extract keywords"""
    article = get_article(url)
    pp.pprint(get_keywords(article['text']))

     
@click.command()
@click.argument('url')
def categories(url):
    """Get category"""
    print 'Getting article...'
    text = get_article(url)['text']
    print 'Getting categories...'
    pp.pprint(classify_text(text))


cli.add_command(content)
cli.add_command(entities)
cli.add_command(keywords)
cli.add_command(categories)
