def resolve_taxon(self, args, context, info):
    '''Resolve taxon and take into consideration which fields are asked for.'''
    from nanoql.utils import get_selection_fields
    from nanoql.api_ena import fetch_taxon, fmt_taxon, taxon_stats

    # use to distinguish which API to call (just taxon info or sequence)
    fields = get_selection_fields(info)
    result = fmt_taxon(
        fetch_taxon(args['key'], fields=fields))
    # use taxid to fetch result from ENA/ GenBank
    # distribute info accross subfields
    # i.e. the meat of all the queries goes here, same for sequences etc.
    # the code below just "distributes" the information among the API fields

    stats = [taxon_stats(result.taxid) if 'stats' in fields else None]
    # TODO: if "stats" in fields, return query
    # http://www.ebi.ac.uk/ena/data/stats/taxonomy/2759

    return [dict(
        name=result.name,
        taxid=result.taxid,
        # name='pseudomonas',
        lineage=result.lineage,  # args['lineage']
        # lineage={'family': 'a', 'genus': 'b'}  # lineage returns 0
        children=result.children[:args['n_children']],
        stats=stats
        )]


def resolve_sequence(self, args, context, info):
    '''Resolve taxon and take into consideration which fields are asked for.'''
    from io import StringIO
    from Bio import SeqIO
    from nanoql.api_ena import fetch_sequence

    # fetch all sequences
    result = fetch_sequence(args['seqid'])
    g = SeqIO.parse(StringIO(result), format='fasta')

    # TODO: turn this into fmt_sequence(..., fmt='fasta') and move to ena_api
    # i.e. don't muddle the resolver logic by stuff it does not really do

    # TODO: if annotation wanted, fetch genbank/ flat file and parse

    return [dict(
        seq=str(i.seq)[:15],
        seqid=i.description
        ) for i in g]



# http://www.ebi.ac.uk/ena/submit/sequence-format
# "flat file" seems to be Genebank format

# FTP
# http://www.ebi.ac.uk/ena/browse/download
# http://www.ebi.ac.uk/ena/browse/sequence-download




# # TODO: separate the requests routines from the resolver. the latter should just choose
# # one based on the context
#
# def resolve_sequence(self, args, context, info):
#     from io import StringIO
#     import requests
#     from Bio import SeqIO
#     from nanoql.objects import Sequence
#
#     print('We want to query', context['db'] + '.')
#     # resolver can be external and then passed to field
#     # http://docs.graphene-python.org/en/latest/types/objecttypes/
#     url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
#     params = {
#         'db': 'nuccore',
#         'id': args['uid'],  # 'KC790373'
#         'rettype': 'fasta',
#         'retmode': 'text',
#         'retmax': args['max']}
#     result = requests.get(url, params)
#     # result = 'ACTAGATACATACATACTACAA'  # for testing
#
#     records = [str(r.seq)[:10] for r in SeqIO.parse(
#         StringIO(result.text), format='fasta')]
#     # seq.format('fasta')
#
#     # we could now turn this result into biopython sequence objects
#     return Sequence(uid=args['uid'], seq=records) # result.text
#
#
# def resolve_taxon(self, args, context, info):
#     from io import StringIO
#     import requests
#     from Bio import SeqIO
#     import xmltodict
#     from nanoql.objects import Taxon
#     from nanoql.utils import url_base, url_append, sanitize_keys, camel_to_snake
#
#     print('We want to query', context['db'] + '.')
#
#     prefix = args['name']
#     params = {'display': 'xml'}
#     url = url_base('taxon') + url_append(params, prefix=args['name'])
#     result = requests.get(url).text
#     d = xmltodict.parse(result)
#
#     return Taxon(
#         taxid=d['ROOT']['taxon']['@taxId'],
#         name=d['ROOT']['taxon']['@scientificName'],
#         parent=d['ROOT']['taxon']['@parentTaxId'],
#         children=[i['@taxId'] for i in d['ROOT']['taxon']['children']['taxon']])
#
# # obj.ROOT.taxon.__dict__.keys()
# # q.ROOT.taxon.children == q.ROOT.taxon.__dict__['children']
# # q.ROOT.taxon.lineage.__dict__
# # q.ROOT.taxon.synonym.__dict__
# # q.ROOT.taxon.children.__dict__
