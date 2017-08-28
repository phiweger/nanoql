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



class SequenceFields(AbstractType):
    seqid = ID()
    seq = String()

    def resolve_seqid(self, args, context, info):
        return self.get('seqid')#

    def resolve_seq(self, args, context, info):
        return self.get('seq')


class Sequence(ObjectType, SequenceFields):
    pass

class InputSequence(InputObjectType, SequenceFields):
    pass



class TaxonFields(AbstractType):
    name = String()
    taxid = ID()  # description='Unique taxonomic identifier.'
    lineage = Field(Lineage)
    children = List(lambda: Taxon)  # see comment below
    stats = String()
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

    def resolve_stats(self, args, context, info):
        return self.get('stats')

class Taxon(ObjectType, TaxonFields):
    pass

class InputTaxon(InputObjectType, TaxonFields):
    lineage = Field(InputLineage)
    children = List(lambda: InputTaxon)
    # if not specified, raises error:
    # InputTaxon.children field type must be Input Type but got: [Taxon].
    pass