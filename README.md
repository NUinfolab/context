# NU Infolab News Context Project

context is a suite of Python based tools for managing contextual knowledge related to web content. This includes resources for article text and metadata extraction from web pages, keyword and named entity extraction, and more.

# About

A number of projects at NU Knightlab involve experiments in the space of evaluating contextual information related to web content in order to enhance user experience. This toolkit brings a number of those explorations into a single project space where they can be further explored and expanded.


# Development

Create an editable installation by running pip install within the cloned repo,
ideally within a virtualenvironment:

```
pip install --editable .
```

This will install the context command line application into your environment.

In order to install lxml, you will need the development packages libxml2 and libxsl:

```
sudo apt-get install libxml2-dev libxslt-dev
```

In order to use the categorizer, you will need to [liblinear](http://www.csie.ntu.edu.tw/%7Ecjlin/liblinear/).

Ubuntu/Debian: ```sudo apt-get install liblinear1```

Mac OS:  should be able to use the included liblinear.so.1


# Running

## Commands

 * context content <url>

# Browser Extensions

To build the browser extensions, you will need to install [Kango](http://kangoextensions.com).

# NLTK Resource requirements

The following resources should be installed with the NLTK downloader:

  * wordnet
  * words
  * maxent_treebank_pos_tagger
  * punkt
  * maxent_ne_chunker
  * stopwords

To use the downloader:

```
>>> import nltk
>>> nltk.download()
```
