# TODO: separate the requests routines from the resolver. the latter should just choose
# one based on the context

def resolve_sequence(self, args, context, info):
    from io import StringIO
    import requests
    from Bio import SeqIO
    from nanoql.objects import Sequence

    print('We want to query', context['db'] + '.')
    # resolver can be external and then passed to field
    # http://docs.graphene-python.org/en/latest/types/objecttypes/
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    params = {
        'db': 'nuccore',
        'id': args['uid'],  # 'KC790373'
        'rettype': 'fasta',
        'retmode': 'text',
        'retmax': args['max']}
    result = requests.get(url, params)
    # result = 'ACTAGATACATACATACTACAA'  # for testing

    records = [str(r.seq)[:10] for r in SeqIO.parse(
        StringIO(result.text), format='fasta')]
    # seq.format('fasta')

    # we could now turn this result into biopython sequence objects
    return Sequence(uid=args['uid'], seq=records) # result.text


def resolve_taxon(self, args, context, info):
    from io import StringIO
    import requests
    from Bio import SeqIO
    import xmltodict
    from nanoql.objects import Taxon
    from nanoql.utils import url_base, url_append, sanitize_keys, camel_to_snake

    print('We want to query', context['db'] + '.')

    prefix = args['name']
    params = {'display': 'xml'}
    url = url_base('taxon') + url_append(params, prefix=args['name'])
    result = requests.get(url).text
    d = xmltodict.parse(result)

    return Taxon(
        uid=d['ROOT']['taxon']['@taxId'],
        name=d['ROOT']['taxon']['@scientificName'],
        parent=d['ROOT']['taxon']['@parentTaxId'],
        children=[i['@taxId'] for i in d['ROOT']['taxon']['children']['taxon']])

# obj.ROOT.taxon.__dict__.keys()
# q.ROOT.taxon.children == q.ROOT.taxon.__dict__['children']
# q.ROOT.taxon.lineage.__dict__
# q.ROOT.taxon.synonym.__dict__
# q.ROOT.taxon.children.__dict__
