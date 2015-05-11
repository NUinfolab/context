from .nlp.entities import collapse_entities
from .nlp.util import quoted_terms


def twitter_query(keywords=None, entities=None):
    """Form a twitter query string from keywords and/or entities.

    TODO: Fix query structure. This does not look like a valid Twitter query. 
    Do we need to fix this?
    See: https://dev.twitter.com/rest/public/search
    """
    q_entities = []
    if entities:
        q_entities = collapse_entities(
            [d for d in entities if d['score'] > 0.01])
    q_keywords = []
    if keywords:
        q_keywords = [d['keyword'] for d in keywords \
            if d['count'] > 2 and d['keyword'] not in q_entities]
    q_keywords = quoted_terms(q_keywords[:5])
    q_entities = quoted_terms(q_entities[:5])   
    q = ''
    if q_keywords and q_entities:
        q = '(%s) AND (%s)' % \
            (' OR '.join(q_keywords), ' OR '.join(q_entities))
    elif q_keywords:
        q = q_keywords.pop(0)
        if len(q_keywords) > 1:
            q += ' AND (%s)' % ' OR '.join(q_keywords)
        elif len(q_keywords) > 0:
            q += ' AND %s' % q_keywords[0]
    elif q_entities:  
        q = q_entities.pop(0)
        if len(q_entities) > 1:
            q += ' AND (%s)' % ' OR '.join(q_entities)
        elif len(q_entities) > 0:
            q += ' AND %s' % q_entities[0]   
    return q

