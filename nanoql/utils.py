def get_selection_fields(info):
    '''Get all fields that are part of the (first-level) query.'''
    # Is a certain field present?
    # https://github.com/graphql-python/graphene/issues/462
    # https://github.com/graphql-python/graphene/issues/431
    sub_fields = []
    for field in info.field_asts:
        for selection in field.selection_set.selections:
            sub_fields.append(selection.name.value)
    return sub_fields


# https://gist.github.com/href/1319371
def convert_to_obj(dictionary, name='GenericDict'):
    '''Convert a dict into a named tuple object.'''
    from collections import namedtuple

    NT = namedtuple(name, dictionary.keys())
    gen_dict = NT(**dictionary)
    return gen_dict


def url_base(key):
    '''Return base urls.

    Example:

    url_base('search')
    # 'http://www.ebi.ac.uk/ena/data/search'

    '''
    d = {'base': 'http://www.ebi.ac.uk/ena/data/',
        'taxon': 'view/Taxon:',
        'project': 'view/Project:',
        'stats_taxon': 'stats/taxonomy/',
        'retrieve': 'view/',
        'search': 'search'}
    return d['base'] + d[key]



def url_append(d, prefix=None):
    '''
    url = 'http://www.ebi.ac.uk/ena/data/view/'
    params = {
        'domain': 'assembly',
        'result': 'assembly',
        'display': 'xml'}
    url += url_append(params, prefix='SOMEID')
    '''
    s = ''
    for k, v in d.items():
        s += '&{}={}'.format(k, v)
    if prefix:
        return str(prefix) + s  # if prefix e.g. tax ID (int) cast to str
    else:
        return s


def sanitize_keys(d, fmt_function):
    '''
    stackoverflow, 11700705

    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        fmt_function (func): function that takes the string in one convention and returns it in the other one.
    Returns:
        Dictionary with the new keys.

    Example:

    \b
    from dotmap import DotMap
    result = xmltodict.parse(requests.get(url).text)
    dm = DotMap(sanitize_keys(result, lambda key: camel_to_snake(key.replace('@', ''))))
    dm.root.taxon.tax_id  # '287'
    dm.root.taxon.taxonomic_division  # 'PRO'
    dm.root.taxon.children.taxon[0].tax_id  # Pseudomonas aeruginosa 2192
    '''
    new = {}

    for k, v in d.items():
        new_v = v
        if isinstance(v, dict):
            new_v = sanitize_keys(v, fmt_function)
        elif isinstance(v, list):
            new_v = list()
            for x in v:
                try:
                    new_v.append(sanitize_keys(x, fmt_function))
                except AttributeError:  # list contains types other than dict
                    new_v.append(x)
        new[fmt_function(k)] = new_v
    return new


def camel_to_snake(name):
    '''stackoverflow, 1175208'''
    import re

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def xmltodotmap(xml):
    '''Turn xml (ugly) into dotmap (pretty).'''
    from dotmap import DotMap
    import xmltodict
    from nanozoo.utils import sanitize_keys, camel_to_snake

    return DotMap(
        sanitize_keys(
            xmltodict.parse(xml),
            lambda key: camel_to_snake(key.replace('@', ''))))


def chunks(l, n):
    '''
    Yield successive n-sized chunks from l (stackoverflow, 312443).
    a = [1, 2, 3, 4]
    list(chunks(a, 2))
    # [[1, 2], [3, 4]]
    Returns empty list if list empty.
    For overlapping chunks, see windows()
    '''
    for i in range(0, len(l), n):
        yield l[i:i + n]