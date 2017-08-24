def fetch_uid(uid=None, name='', context=None, max_n_records=None):
    '''Fetch sequence data from <context>.

    max_n_records .. None means all

    Example:

    result = fetch_uid(uid=['KC790373', 'KC790374'], context='ncbi')
    '''

    import requests

    if context == 'ncbi':
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        params = {
            'db': 'nuccore',
            'id': uid,  # 'KC790373'
            'rettype': 'fasta',
            'retmode': 'text',
            'retmax': max_n_records}  # if arg is None, requests wont include it
        result = requests.get(url, params)
        return result
    else:
        raise ValueError('Not yet implemented.')


def fmt_fasta(result):
    '''Format the requests result.

    Example:

    from nanohq.restapi import fetch_uid, fmt_fasta

    result = fetch_uid(uid=['KC790373', 'KC790374'], context='ncbi')
    a = fmt_fasta(result)
    next(a)  # ('KC790373.1', 'ATGGGGAACA')
    '''
    from io import StringIO
    from Bio import SeqIO

    for read_ in SeqIO.parse(StringIO(result.text), format='fasta'):
        # read_ as to not override builtin read()
        yield read_.description.split(' ')[0], str(read_.seq)[:20]


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

    lineage = defaultdict(dict)  # a dict of dicts
    for i in d['ROOT']['taxon']['lineage']['taxon']:
        try:
            lineage[i['@rank']] = i['@scientificName']
            # no taxid for now, to keep it minimal
        except KeyError:  # root does not have a rank -- discarded
            pass
    # del lineage['class']  # just for now, has name conflicts w/ python

    children = []
    for i in d['ROOT']['taxon']['children']['taxon']:
        try:
            children.append({
                'taxid': i['@taxId'],
                'name': i['@scientificName']
                })
        except KeyError:
            pass


    return convert_to_obj({
        'taxid': d['ROOT']['taxon']['@taxId'],                # taxid
        'name': d['ROOT']['taxon']['@scientificName'],        # name
        'parent': d['ROOT']['taxon']['@parentTaxId'],         # parent taxid
        'children': children,
        'lineage': lineage
        }, name='ResultTaxon')