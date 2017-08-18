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
    import untangle
    from nanoql.objects import Taxon
    from nanoql.utils import url_base, url_append, sanitize_keys, camel_to_snake

    print('We want to query', context['db'] + '.')

    prefix = args['name']
    params = {'display': 'xml'}
    url = url_base('taxon') + url_append(params, prefix=args['name'])
    result = requests.get(url).text
    obj = untangle.parse(result)

    return Taxon(
        uid=obj.ROOT.taxon['taxId'],
        name=obj.ROOT.taxon['scientificName'])