def suggest(name, n=None):
    '''Find the first <n> searchable taxa starting with <name>.

    Note that ENA only searches for the <name> at the beginning of a group
    of words, e.g. we could search for "Semliki forest virus" by "semliki"
    but not "forest virus".

    Example:

    >>> suggest('semliki', 10)
        [{'displayName': 'Semliki Forest virus',
        'scientificName': 'Semliki Forest virus',
        'taxId': '11033'}, ...
    '''
    import requests

    url = 'http://www.ebi.ac.uk/ena/data/taxonomy/v1/taxon/suggest-for-search/'
    url += name
    if n:  # If n not specified, return all results.
        url += '?limit=' + str(n)

    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise ValueError('Query name not found.')


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


def fetch_sequence(key=[], fmt='fasta'):
    '''Given a sequence ID (accession number), fetch the source in <format>.

    TODO:

    - need CLI interface

    nanoql explore
    nanoql fetch --query query.ql --args args.json --out all_viruses.fasta

    - rate limit? see comments below
    - parallel execution? see:
        - https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html
        - http://terriblecode.com/blog/asynchronous-http-requests-in-python/
        - https://github.com/kennethreitz/grequests
        - https://github.com/ross/requests-futures
        - in golang?: https://gist.github.com/mattetti/3798173
        - use all viral sequences and benchmark
    - displax text (flat file, genbank format):
        - http://www.ebi.ac.uk/ena/data/view/AACH01000027%26display%3Dtext
    - if nothing found for a str in the accession number list, say so
    '''
    import requests
    from nanoql.utils import url_base, url_append, chunks

    # get information on the taxon

    # if not 'children' in fields: # we can use the nice taxon API at
    #     base = 'http://www.ebi.ac.uk/ena/browse/taxon/v1/'

    # to retrieve associated sequences

    # split sequences into chunks of length 1000
    # get async


    params = {'display': fmt}
    url = url_base('retrieve') + url_append(params, prefix=','.join(key))
    # http://www.ebi.ac.uk/ena/data/view/Taxon:2759 or
    # http://www.ebi.ac.uk/ena/data/view/2759 -- both works
    result = requests.get(url).text
    return result


# http://www.ebi.ac.uk/ena/browse/data-retrieval-rest#pagination_options
# There is an additional limit parameter which is used to safe-guard the system and the user from unintentional download of millions of sequences. The limit sets the maximum number of records that can be downloaded and if not set will default to 100,000. To increase the maximum, set the limit to a larger number, for example:
# http://www.ebi.ac.uk/ena/data/view/CEQY01000001-CEQY01396425&display=fasta&download=gzip&limit=400000
#
# We advise that you increase the limit with caution.  Downloading very large numbers of very large sequences can result in more problems than downloading your set in batches, especially if you have a slower network connection.

