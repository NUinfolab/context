from .nlp.entities import collapse_entities
from .nlp.util import quoted_terms


def twitter_query(keywords=None, entities=None):
    """
    Form a twitter query string from keywords and/or entities.
    See: https://dev.twitter.com/rest/public/search
    
    Testing shows that OR has precedence over AND:
    
    a b OR c d      is          a AND (b OR c) AND d
                    is not      (a AND b) OR (c AND d)
      
    a OR b c OR d   is          (a OR b) AND (c OR d)
                    is not      a OR (b AND c) OR d
                                  
    For example, the query:
    
        free OR good beer OR shirt
    
    is interpreted as:
    
        (free OR good) AND (beer OR shirt)
        
    so it will return tweets containing:
    
                "free" and "beer"
        or      "free" and "shirt"
        or      "good" and "beer"
        or      "good" and "shirt"
            
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
        # at least one keyword and at least one entity
        q = '%s %s' % \
            (' OR '.join(q_keywords), ' OR '.join(q_entities))
    elif q_keywords:
        # top keyword and at least one other keyword
        q = q_keywords.pop(0)
        if len(q_keywords) > 0:
            q += ' %s' % ' OR '.join(q_keywords)
    elif q_entities:  
        # top entity and at least one other entity
        q = q_entities.pop(0)
        if len(q_entities) > 0:
            q += ' %s' % ' OR '.join(q_entities)
    return q
