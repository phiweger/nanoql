import json
import graphene
from graphene import AbstractType, InputObjectType, ObjectType, String, ID, Field, List



class LineageFields(AbstractType):
    family = String()
    genus = String()

    def resolve_family(self, args, context, info):
        return self.get('family')

    def resolve_genus(self, args, context, info):
        return self.get('genus')


class Lineage(ObjectType, LineageFields):
    pass

class InputLineage(InputObjectType, LineageFields):
    pass


# class ChildFields(AbstractType):
#     taxid = ID()
#     seq = String()
#
#     def resolve_taxid(self, args, context, info):
#         return self.get('taxid')
#
#     def resolve_seq(self, args, context, info):
#         return self.get('seq')
#
# class Child(ObjectType, ChildFields):
#     pass
#
# class InputChild(InputObjectType, ChildFields):
#     pass


class TaxonFields(AbstractType):
    name = String()
    lineage = Field(Lineage)
    children = List(lambda: Taxon)
    # graphene issue 110, 436, 522
    # graphene-sqlalchemy issue 18

    def resolve_name(self, args, context, info):
        return self.get('name')

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
    taxon = List(
        Taxon,
        name=String(),
        lineage=InputLineage(),
        children=List(InputTaxon)   # recursive objects, graphene issue 110
        )

    def resolve_taxon(self, args, context, info):
        # use taxid to fetch result from ENA/ GenBank
        # distribute info accross subfields
        # i.e. the meat of all the queries goes here, same for sequences etc.
        # the code below just "distributes" the information among the API fields
        return [dict(
            name=args['name'],
            # name='pseudomonas',
            lineage=args['lineage'],
            # lineage={'family': 'a', 'genus': 'b'}  # lineage returns 0
            children=[{'name': 'c'}, {'name': 'd'}]
            )]

schema = graphene.Schema(query=Query)

'''
query {
  taxon(name: "pseudomonas", lineage: {family: "a", genus: "b"}) {
    name
    lineage {
      genus
    }
    children {
      name
    }
  }
}


query {
  taxon(name: "pseudomonas") {
    name
    lineage {
      family,
      genus
    }
    children
  }
}
'''

'''
query {
  taxon(name: "pseudomonas", lineage: {family: "a", genus: "b"}) {
    name
    lineage {
      family
      genus
    }
  }
}
'''


'''
query(...) {
    assembly {
        contigs
        metadata
    }
    reads {
        sra_id
    }
    taxon {
        taxid
        name
        parent
        children {
            taxid
            name
        }
        lineage {
            family
            genus
        }
    }
}
'''

