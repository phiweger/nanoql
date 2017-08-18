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