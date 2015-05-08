# -*- coding: utf-8 -*-
"""Partly based on this article:
http://timmcnamara.co.nz/post/2650550090/extracting-names-with-6-lines-of-python-code"""
from __future__ import division
from collections import defaultdict, namedtuple
import codecs
import nltk
from .util import get_sentences, pos_tag, tokenize, NLTK_VERSION


EntityKey = namedtuple('EntityKey', ('tokenized_name', 'normalized_name'))

# TODO: These should go into configuration
KNOWN_ENTITIES = {
    (u'Home', u'Depot'): {
        'name': 'Home Depot',
        'type': 'ORGANIZATION'
    },
    (u'Fox', u'News'): {
        'name': 'Fox News',
        'type': 'ORGANIZATION'
    },
}

NAME_PREFIXES = (
    'mr',
    'mrs',
    'ms',
    'miss',
    'dr',
    'doctor',
    'sgt',
    'sergeant',
    'rev',
    'reverend',
    'chief',
    'executive',
    'officer',
    'president',
)

ORGANIZATION_SUFFIXES = (
    'Academy',
    'Administration',
    'Co',
    'College',
    'Corp',
    'Department',
    'Dept',
    'Herald',
    'Inc',
    'LLC',
    'LTD',
    'Organization',
    'Organisation',
    'Party',
    'Police',
    'Standard',
    'Times',
    'Tribune',
    'University',
    'administration',
    'organisation',
)

LOCATION_SUFFIXES = (
    'Ave.',
    'Avenue',
    # 'Dr.', how to disambiguate?, also St.
    'Drive',
    'Street', 
)

entity_chunk_grammar = r"""
  GPE: {<GPE>+<NNPX_|PERSON>+}
  PERSON: {<NNPX_|PERSON>+<PERSON>}
  PERSON: {<PERSON><NNPX_|PERSON|ORGANIZATION>+}
  ORGANIZATION: {<NNPX_|GPE|PERSON>+<CO_>}
  ORGANIZATION: {<^|DTX_>?<GPE|ORGANIZATION>*<ORGANIZATION>+(<IN>?<DT|GPE|ORGANIZATION|NNPX_|PERSON>)*<CO_>?}
  LOCATION: {<NNPX_|GPE|PERSON>+LOC_}
"""


def chunk_named_entities(tagged_tokens):
    """Use NLTK's named entity chunker to chunk list of tagged tokens"""
    return nltk.ne_chunk(tagged_tokens)
    

def normalize_name(tokens):
    """Normalize tokenized name""" 
    for i, t in enumerate(tokens):
        if t.lower().strip().strip('.') not in NAME_PREFIXES:
            break 
    l = tokens[i:]
    r = ' '.join(l)
    if r.endswith("'s") or r.endswith(codecs.decode("’s", 'utf-8')):
        r = r[:-2] 
    return r


def clean_token(token):
    """Replace fancy single quote with plain single quote"""
    token = token.replace(codecs.decode('’', 'utf-8'), "'")
    return token


def best_name(tokenized_names):
    """Return the most singular item from a list of tokenized names"""
    names = [normalize_name(name) for name in tokenized_names
        if normalize_name(name)]
    if not names:
        return None
    names.sort(lambda x,y: cmp(len(x), len(y)))
    return names[-1]


def entity_score(count, occurrences, sentences):
    """Compute entity score"""
    return ( count / len(sentences) / min(occurrences) )


def retagger(chunk):
    chunk = (clean_token(chunk[0]), chunk[1])
    if chunk[1] == 'NNP' and chunk[0][0].isupper():
        chunk = (chunk[0], 'NNPX_')
    if chunk[0] in LOCATION_SUFFIXES:
        chunk = (chunk[0], 'LOC_')
    if chunk[0][0].isupper() and (
            chunk[0].endswith('istan') or \
            chunk[0].endswith('abad') ):
        chunk = (chunk[0], 'GPE')
    if chunk[0].strip('.') in ORGANIZATION_SUFFIXES:
        chunk = (chunk[0], 'CO_')
    if chunk[0] in ('The',):
        chunk = (chunk[0], 'DTX_')
    return chunk


def retag(chunks):
    for chunk in chunks:
        if isinstance(chunk, tuple):
            yield(retagger(chunk))
        elif hasattr(chunk, 'leaves'):
            if NLTK_VERSION >= 3:
                c = nltk.tree.Tree(chunk.label(), [])
            else:
                c = nltk.tree.Tree('(%s)' % chunk.node)
            for leaf in chunk.leaves():
                newt = retagger(leaf)
                c.append(leaf)
                if newt[1] == 'CO_':
                    if NLTK_VERSION >= 3:
                        c.set_label('ORGANIZATION')
                    else:
                        c.node = 'ORGANIZATION'
                if newt[1] == 'LOC_':
                    if NLTK_VERSION >= 3:
                        c.set_label('LOCATION')
                    else:
                        c.node = 'LOCATION'
            yield c
        else:
            yield chunk


def _entity_types_and_locations(sentences):
    entities_by_type = defaultdict(list)
    locations = {}
    for sentnum, sent in enumerate(sentences, start=1):
        sent = pos_tag(tokenize(sent))
        chunks = chunk_named_entities(sent)
        chunks = [chunk for chunk in retag(chunks)]
        parser = nltk.RegexpParser(entity_chunk_grammar)
        parsed = parser.parse(chunks)
        for chunk in parsed:
            if not isinstance(chunk, nltk.tree.Tree):
                continue
            tokenized_name = tuple([c[0] for c in chunk.leaves()])
            e = KNOWN_ENTITIES.get(tokenized_name)
            if e:
                entity_key = EntityKey(tokenized_name=tokenized_name,
                    normalized_name=e['name'])
                entities_by_type[e['type']].append(entity_key)
            else:
                entity_key = EntityKey(tokenized_name=tokenized_name,
                    normalized_name=normalize_name(tokenized_name))
                if NLTK_VERSION >= 3:
                    entities_by_type[chunk.label()].append(entity_key)
                else:
                    entities_by_type[chunk.node].append(entity_key)
            if entity_key not in locations:
                locations[entity_key] = sentnum
    return entities_by_type, locations


def _organize_entities(entities_by_type, locations, sentences):
    all_entities = []
    for entity_type, entities in entities_by_type.items():
        type_entities = {}
        entities.sort(lambda x,y: cmp(len(y.normalized_name),
            len(x.normalized_name)))
        for i, entity in enumerate(entities):
            if entity in type_entities:
                type_entities[entity]['count'] += 1
            else:
                candidate_matches = []
                for key, count in type_entities.items():
                    if entity.normalized_name in key.normalized_name:
                        candidate_matches.append(key)
                if len(candidate_matches) == 1:
                    type_entity = type_entities[candidate_matches[0]]
                    type_entity['count'] += 1
                    if not entity.tokenized_name in type_entity['name_forms']:
                        type_entity['name_forms'].append(
                            entity.tokenized_name)
                        type_entity['locations'].append(locations[entity])
                else:
                    type_entities[entity] = {
                        'count': 1,
                        'name_forms': [ entity.tokenized_name ],
                        'locations': [ locations[entity] ]
                    }
        for entity_key, entity_data in type_entities.items():
            name = best_name(entity_data['name_forms'])
            if name:
                all_entities.append({
                    'name': name,
                    'type': entity_type,
                    'name_forms': [' '.join(form) for form in
                        entity_data['name_forms']],
                    'score': entity_score(
                        entity_data['count'],
                        entity_data['locations'],
                        sentences)
                })
    return all_entities


def get_entities(text):
    """Return list of entities in text sorted by score (desc)"""
    sentences = get_sentences(text)
    entities_by_type, locations = _entity_types_and_locations(sentences)
    all_entities = _organize_entities(entities_by_type, locations, sentences)
    sorted_entities = sorted(
        all_entities, key=lambda x: x['score'], reverse=True)
    names = [ entity['name'] for entity in sorted_entities ]
    indexes_to_delete = []
    # Keep only the top scoring of repeated names. TODO: Consider better
    # options, e.g. checking against known GPE, ORGANIZATION lists. 
    for i, name in enumerate(names):
        if name in names[:i]:
            indexes_to_delete.append(i)
    for i in reversed(indexes_to_delete):
        del(sorted_entities[i]) 
    return sorted_entities


def collapse_entities(entity_list):
    """Return unique list of entity names collapsed into shortest forms"""
    name_list = []
    
    for e in entity_list:
        name_forms = sorted(e['name_forms'], key=lambda s: len(s))
        while name_forms:
            name = name_forms.pop(0)                   
            for i in range(len(name_forms) - 1, -1, -1):
                s = name_forms[i]
                if s.find(name) > -1:
                    del name_forms[i]   
            if name not in name_list:                
                name_list.append(name)
        name_list.extend([s for s in name_forms if s not in name_list])
       
    return name_list
