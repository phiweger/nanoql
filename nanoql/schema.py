'''
Use case: Given a list of accession ids, get both taxonomic info and sequence info from it. Sequence can be raw reads, assembly (curation level 1) or annotation (curation level 2).

https://stackoverflow.com/questions/39381436/graphql-django-resolve-queries-using-raw-postgresql-query

https://github.com/graphql-python/graphene/issues/462
https://github.com/graphql-python/graphene/issues/431
'''


from graphene import Schema, ObjectType
from graphene import Int, String, ID, Field, List

from nanoql.fields import Lineage, InputLineage
from nanoql.fields import Taxon, InputTaxon
from nanoql.fields import Sequence, InputSequence
from nanoql.resolver import resolve_taxon, resolve_sequence, resolve_suggest


class Query(ObjectType):
    taxon = List(  # do we need a list?
        Taxon,
        # all the following are arguments, i.e. in the query: taxon(<arguments>){...}
        description='Description of the entire class',
        key=ID(
            description='(Synonymous/ approximate) name or NCBI ID of taxon.',
            default_value=42),
        n_children=Int(
            description='The number of children to return.',
            default_value=int(1e6)),  # basically "all"
        resolver=resolve_taxon)

    sequence = List(
        Sequence,
        description='Sequence field.',
        seqid=List(
            ID,
            description='A list of sequence accession IDs.',
            required=True),
        resolver=resolve_sequence)

    suggest = List(
        Taxon,
        description='Let ENA suggest possible name matches.',
        key=ID(
            description='Taxon name prefix.',
            default_value='cat'),
        n_records=Int(
            description='The number of children to return.',
            default_value=int(1e6)),  # basically "all"
        resolver=resolve_suggest)

schema = Schema(query=Query, auto_camelcase=False)

# The next part is wrapped by the app. TODO: How to save it though?
# query = '''
#     query {
#       taxon(name: "pseudomonas aeruginosa") {
#         taxid
#         name
#         parent
#         children
#       }
#     }
# '''
# e = schema.execute(query, context_value={'db': 'genbank'})
# e.data, e.errors, e.invalid

# Some example queries.
'''
{
  taxon(key: "Pseudomonas aeruginosa", n_children: 4) {
    taxid
    stats
    name
    lineage {
      family
      order
      cls
      phylum
    }
    children {
      name
      taxid
    }
  }
}


{
  taxon(key: 287) {
    stats
  }
}


# nice error messages
{
  taxon(key: 278) {
    stats
  }
}

{
  sequence(seqid: ["AACH01000026", "AACH01000027"]) {
    seqid
    seq
  }
}

{
  suggest(key: "semliki", n_records: 4) {
    taxid
    name
  }
}
# can then be turned into "taxon" quickly
'''

