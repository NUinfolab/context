# NU Infolab News Context Project

context is a suite of Python based tools for managing contextual knowledge related to web content. This includes resources for article text and metadata extraction from web pages, keyword and named entity extraction, and more.

The primary entry point is a Flask based web application that serves both HTML and JSON payloads. This application is located in the web directory.

context itself, under the context directory, may also be used directly as a python library.  

# About

A number of projects at NU InfoLab involve experiments in the space of evaluating contextual information related to web content in order to enhance user experience. This toolkit brings a number of those explorations into a single project space where they can be further explored and expanded.


# Requirements

In order to install lxml, you will need the development packages libxml2 and libxsl:

```
sudo apt-get install libxml2-dev libxslt-dev
```

In order to use the categorizer, you will need to [liblinear](http://www.csie.ntu.edu.tw/%7Ecjlin/liblinear/).

Ubuntu/Debian: ```sudo apt-get install liblinear1```

Mac OS:  should be able to use the included liblinear.so.1


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
