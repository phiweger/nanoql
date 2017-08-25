def fetch_taxon(key=None, fields=None):
    '''Given a taxonomic name, fetch scientific name and some taxonomic info.

    API:

    - taxon info: http://www.ebi.ac.uk/ena/browse/taxonomy-service
    - associated seqs: http://www.ebi.ac.uk/ena/browse/taxon-portal-rest
    - stats: http://www.ebi.ac.uk/ena/data/stats/taxonomy/2759
    '''
    import requests
    from nanoql.utils import url_base, url_append

    # get information on the taxon

    # if not 'children' in fields: # we can use the nice taxon API at
    #     base = 'http://www.ebi.ac.uk/ena/browse/taxon/v1/'

    # to retrieve associated sequences
    params = {'display': 'xml'}
    url = url_base('taxon') + url_append(params, prefix=key)
    # http://www.ebi.ac.uk/ena/data/view/Taxon:2759 or
    # http://www.ebi.ac.uk/ena/data/view/2759 -- both works
    result = requests.get(url).text
    return result


def fmt_taxon(result):
    '''
    Example:

    next(fmt_taxon(fetch_taxname('pseudomonas aeruginosa')))

    '''
    from collections import defaultdict
    import xmltodict
    from nanoql.utils import convert_to_obj

    d = xmltodict.parse(result)

    # TODO: if empty, return possible results from approximate search

    try:
        d['ROOT']['taxon']
    except KeyError:
        raise KeyError(
            'Error during request with url [...]' + d['ROOT']['@request'], d['ROOT']['#text'])

    lineage = defaultdict(dict)  # a dict of dicts
    try:
        lin = d['ROOT']['taxon']['lineage']['taxon']
        for i in lin:
            try:
                lineage[i['@rank']] = i['@scientificName']
                # no taxid for now, to keep it minimal
            except KeyError:  # root does not have a rank -- discarded
                pass
    except KeyError:  # no lineage for query
        pass
    # del lineage['class']  # just for now, has name conflicts w/ python

    children = []
    try:
        ch = d['ROOT']['taxon']['children']['taxon']
        for i in ch:
            try:
                children.append({
                    'taxid': i['@taxId'],
                    'name': i['@scientificName']
                    })
            except KeyError:  # certain lineage categories not present
                pass
    except KeyError:  # no children for query
        pass

    return convert_to_obj({
        'taxid': d['ROOT']['taxon']['@taxId'],                # taxid
        'name': d['ROOT']['taxon']['@scientificName'],        # name
        'parent': d['ROOT']['taxon']['@parentTaxId'],         # parent taxid
        'children': children,
        'lineage': lineage
        # TODO: return search url for debugging
        }, name='ResultTaxon')


def taxon_stats(taxid):
    '''Get a table of search results and the associated ENA portal for a given taxid.

    Returns a json string.

    Example:

    >>> taxon_stats(287)
    '{"noncoding_release":50194,"coding_update":804503,...}'
    '''
    from io import StringIO
    import json
    import requests
    import pandas as pd

    header = 'taxon taxon_bases descendants descendants_bases'.split(' ')

    url = 'http://www.ebi.ac.uk/ena/data/stats/taxonomy/' + str(taxid)
    result = pd.read_csv(
        StringIO(requests.get(url).text),
        sep='\t\t\t',  # OMFG, really? Triple tab?
        engine='python',
        index_col=0)
    result.columns = header
    return result['taxon'].to_json(force_ascii=False)