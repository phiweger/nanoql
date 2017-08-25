import graphene as gp
from nanoql.resolver import resolve_sequence


class Sequence(gp.ObjectType):
    uid = gp.List(gp.String)  # ...(description='A typical hello world')
    seq = gp.List(gp.String)

class InputSequence(gp.InputObjectType):
    username = gp.String()
    first_name = gp.String()

class Taxon(gp.ObjectType):
    taxid = gp.String()
    uid = gp.String()
    name = gp.String()
    parent = gp.String()
    children = gp.List(gp.Int)
    sequence = gp.Field(  # InputFields
        Sequence,
        resolver=resolve_sequence)

    def resolve_uid(self, args, context, info):
        return self.get('uid')

    # this seems very inefficient, think DRY
    # https://github.com/graphql-python/graphene/issues/221
    # sequence = graphene.Field(Sequence)  # or lambda: Sequence
    # http://docs.graphene-python.org/en/latest/execution/dataloader/