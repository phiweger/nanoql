'''
Use case: Given a list of accession ids, get both taxonomic info and sequence info from it. Sequence can be raw reads, assembly (curation level 1) or annotation (curation level 2).

https://stackoverflow.com/questions/39381436/graphql-django-resolve-queries-using-raw-postgresql-query

https://github.com/graphql-python/graphene/issues/462
https://github.com/graphql-python/graphene/issues/431
'''


import json

import graphene
from graphene import AbstractType, InputObjectType, ObjectType
from graphene import Int, String, ID, Field, List


class LineageFields(AbstractType):
    cls = String()  # "class" as field name conflict with python, i.e. reserved keyword
    order = String()
    phylum = String()
    subphylum = String()
    suborder = String()
    superkingdom = String()
    family = String()

    def resolve_family(self, args, context, info):
        return self.get('family')#

    def resolve_cls(self, args, context, info):
        return self.get('class')

    def resolve_order(self, args, context, info):
        return self.get('order')

    def resolve_phylum(self, args, context, info):
        return self.get('phylum')

    def resolve_suborder(self, args, context, info):
        return self.get('suborder')

    def resolve_subphylum(self, args, context, info):
        return self.get('subphylum')

    def resolve_superkingdom(self, args, context, info):
        return self.get('superkingdom')

class Lineage(ObjectType, LineageFields):
    pass

class InputLineage(InputObjectType, LineageFields):
    pass


class TaxonFields(AbstractType):
    name = String()
    taxid = ID()  # description='Unique taxonomic identifier.'
    lineage = Field(Lineage)
    children = List(lambda: Taxon)
    description = 'Taxonomic information.'
    # use of lambda prevents circular import errors
    # see graphene issues 110, 436, 522
    # and graphene-sqlalchemy issue 18

    def resolve_name(self, args, context, info):
        return self.get('name')

    def resolve_taxid(self, args, context, info):
        return self.get('taxid')

    def resolve_lineage(self, args, context, info):
        return self.get('lineage')

    def resolve_children(self, args, context, info):
        return self.get('children')

class Taxon(ObjectType, TaxonFields):
    pass

class InputTaxon(InputObjectType, TaxonFields):
    lineage = Field(InputLineage)
    children = List(lambda: InputTaxon)
    # if not specified, raises error:
    # InputTaxon.children field type must be Input Type but got: [Taxon].
    pass


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
            default_value=int(1e6))  # basically "all"
        )

    def resolve_taxon(self, args, context, info):
        '''Resolve taxon and take into consideration which fields are asked for.'''
        from nanoql.utils import get_selection_fields
        from nanoql.restapi import fetch_taxon, fmt_taxon

        # use to distinguish which API to call (just taxon info or sequence)
        result = fmt_taxon(
            fetch_taxon(args['key'], fields=get_selection_fields(info)))
        # use taxid to fetch result from ENA/ GenBank
        # distribute info accross subfields
        # i.e. the meat of all the queries goes here, same for sequences etc.
        # the code below just "distributes" the information among the API fields
        return [dict(
            name=result.name,
            taxid=result.taxid,
            # name='pseudomonas',
            lineage=result.lineage,  # args['lineage']
            # lineage={'family': 'a', 'genus': 'b'}  # lineage returns 0
            children=result.children[:args['n_children']]
            )]

schema = graphene.Schema(query=Query, auto_camelcase=False)

'''
{
  taxon(key: "pseudomonas aeruginosa", n_children: 2) {
    taxid
    lineage {
      family
      order
      cls
    }
    children {
      name
      taxid
    }
  }
}

{
  taxon(key: "Pseudomonas aeruginosa 2192", n_children: 4) {
    taxid
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
'''

