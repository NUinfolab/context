from .util import quoted_terms


def twitter_disjunct_query(terms):
    terms = quoted_terms(terms)[:5] # TODO: We actually need to limit this
                                    # to 10 overall keywords & operators
    return ' OR '.join(terms)

