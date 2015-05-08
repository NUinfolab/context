# -*- coding: utf-8 -*-
import codecs
import os
import unittest
import context.nlp.entities

cwd = os.path.dirname(os.path.realpath(__file__))

def path(relpath):
    return os.path.join(cwd, relpath)

ARTICLES = [ {
    'path': path('data/content/bloomberg.com.2014-10-06.ebola.txt'),
    'url': 'http://www.bloomberg.com/news/2014-10-06/ebola-screening-at-u-s-airports-in-review-cdc-director.html',
    'entities': { 
        'U.S.': 'GPE',
        'West Africa': 'LOCATION',
        'Ebola': 'ORGANIZATION',
        'Thomas Frieden': 'PERSON',
        'African': 'ORGANIZATION',
        'The Obama administration': 'ORGANIZATION',
        'White House': 'FACILITY',
        'Dallas': 'GPE',
        'Centers for Disease Control': 'ORGANIZATION',
        "Barack Obama's administration": 'ORGANIZATION',
        'Liberian': 'GPE',
        'CNN': 'ORGANIZATION',
        'Frieden': 'GPE',
        'Duncan': 'GPE',
        'Thomas Eric Duncan': 'PERSON',
        'Africa': 'GPE',
        'Ohio Republican': 'ORGANIZATION',
        'Senator Rob Portman': 'PERSON',
        'The New York Times': 'ORGANIZATION',
        'Gary Kelly': 'PERSON',
        'European': 'GPE',
        'Sierra Leone': 'PERSON',
        'Guinea': 'GPE',
        'Lisa Monaco': 'PERSON',
        'Elizabeth Wasserman': 'PERSON',
        'Americans': 'GPE',
        'Southwest Airlines Co.': 'ORGANIZATION',
        'Southwest': 'PERSON',
        'Caribbean': 'LOCATION',
        'Mexico': 'GPE',
        'FAA': 'ORGANIZATION',
        'Washington': 'GPE',
        'Jon Morgan': 'PERSON',
      }
  }, {
    'path': path('data/content/nytimes.com.2014-10-08.isis-syria.txt'),
    'url': 'http://www.nytimes.com/2014/10/08/world/middleeast/isis-syria-coalition-strikes.html',
    'entities': {
        'Turkey': 'GPE',
        'Kobani': 'GPE|PERSON',
        'Recep Tayyip Erdogan': 'PERSON',
        'Syria': 'GSP',
        'United States': 'GPE',
        'Turkish': 'GSP',
        'Bashar al-Assad': 'PERSON',
        'American': 'GPE',
        'MURSITPINAR': 'GPE',
        'Kurdish': 'GPE',
        'Washington': 'GPE',
        'Obama': 'PERSON',
        'Gaziantep': 'GPE',
        'ISIS': 'ORGANIZATION',
        'Ain al-Arab': 'PERSON',
        'ISIL': 'ORGANIZATION',
        'Residents': 'PERSON',
        'Barwar Mohammad Ali': 'PERSON',
        'Suruc': 'GPE',
        'Avni Altindag': 'PERSON',
        'Ali': 'PERSON',
        'Mahmoud Nabo': 'PERSON',
        'Mustafa Bali': 'PERSON',
        "Kurdistan Workers' Party": 'ORGANIZATION',
        'Tear': 'PERSON',
        'Ali Kor': 'PERSON',
        'Buses': 'PERSON',
        'Young': 'GPE',
      }
    }, {
    'path': path('data/content/bloomberg.com.2014-10-06.jobless-rate.txt'),
    'url': 'http://www.bloomberg.com/news/2014-10-03/jobless-rate-in-u-s-falls-to-5-9-in-september-payrolls-jump.html',
    'entities': { 
        'U.S.': 'GPE',
        'Washington': 'GPE',
        'Labor Department': 'ORGANIZATION',
        'Bloomberg': 'PERSON',
        'Dean Maki': 'PERSON',
        'Naveed Siddiqui': 'PERSON',
        'Barclays PLC in New York': 'ORGANIZATION',
        'Sustained': 'PERSON',
        'Stocks': 'PERSON',
        'New York': 'GPE',
        'The Standard': 'ORGANIZATION',
        'Cessna': 'GPE',
        'Bell Helicopter': 'ORGANIZATION',
        'Textron Inc.': 'ORGANIZATION',
        'Americans': 'GPE',
        'Textron': 'PERSON',
        'University of Maryland': 'ORGANIZATION',
        'August': 'GPE',
        'The Fed': 'ORGANIZATION',
        'Norfolk': 'GPE',
        'Brown': 'GPE',
        'Drew': 'PERSON',
        'Baltimore': 'GPE',
        'Fed': 'GPE',
        'Policy': 'GPE',
        'Fed Chair Janet Yellen': 'PERSON',
        'Southern': 'LOCATION',
        'Jim Squires': 'PERSON',
        'Automotive Group': 'ORGANIZATION',
        'Commerce Department': 'ORGANIZATION',
        'Household': 'GPE',
        'Institute for Supply Management': 'ORGANIZATION',
        'Emily Kolinski Morris': 'PERSON',
        'Ford Motor Co.': 'ORGANIZATION',
        'Lorraine Woellert': 'PERSON',
        'Carlos Torres': 'PERSON',
        'Brendan Murray': 'PERSON',
        'Mark Rohner': 'PERSON', 
    }
  }, {
    'path': path('data/content/foxnews.com.2014-10-07.isis.txt'),
    'url': 'http://www.foxnews.com/world/2014/10/07/isis-reportedly-enters-strategic-syrian-town-near-turkish-border/',
    'entities': { 
        'Turkish President Recep Tayyip Erdogan': 'GPE',
        'Syrian President Bashar Assad': 'GPE',
        'Syria': 'GSP',
        'Islamic State': 'ORGANIZATION',
        'ISIS': 'ORGANIZATION',
        'Kobani': 'PERSON',
        'Turkish': 'GSP',
        'De Mistura': 'PERSON',
        'Iraq': 'GPE',
        'Turkey': 'GPE',
        'UN Special Envoy': 'ORGANIZATION',
        'The Associated Press': 'ORGANIZATION',
        'Kurdish': 'GPE',
        'Ankara': 'GPE',
        'U.S.': 'GPE',
        'Fox News': 'ORGANIZATION',
        'Gaziantep': 'GPE',
        'Erdogan': 'PERSON',
        'Reuters': 'ORGANIZATION',
        'Aleppo': 'PERSON',
        'Raqqa': 'ORGANIZATION',
        'The New York Times': 'ORGANIZATION',
        'Ayn Arab': 'PERSON',
        'Arabic': 'ORGANIZATION',
        'AP': 'ORGANIZATION',
        'People': 'ORGANIZATION',
        'YPG': 'ORGANIZATION',
        'Protection Units': 'ORGANIZATION',
        'Wall Street Journal': 'LOCATION',
        'Kurds': 'PERSON',
        'Syrian Observatory': 'PERSON',
        'Human Rights': 'ORGANIZATION',
        'State Department': 'ORGANIZATION',
        'White House': 'FACILITY',
        'Retired Marine Gen. John Allen': 'PERSON', 
        'Istanbul': 'GPE',
        'Dogan': 'ORGANIZATION',
        'Diyarbakir': 'GPE',
        'Van': 'PERSON',
        'Hakkari': 'PERSON',
        'Sirnak': 'PERSON',
        'Sanliurfa': 'PERSON',
        'Batman': 'PERSON',
        'Greg Palkot': 'PERSON'
    }
  }
]


class EntitiesTestCase(unittest.TestCase):

    def test_entity_extractions(self):
        for article in ARTICLES:
            text = codecs.open(article['path'], encoding='utf-8').read()
            entity_data = context.nlp.entities.get_entities(text)
            entity_types = { e['name']:e['type'] for e in entity_data }
            for name, type_ in article['entities'].items():
                self.assertTrue(name in entity_types.keys(), name)
                self.assertTrue(entity_types[name] in type_, name + '/' + entity_types[name])
