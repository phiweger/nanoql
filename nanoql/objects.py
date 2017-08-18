import graphene
from nanoql.resolver import resolve_sequence


class Sequence(graphene.ObjectType):
    uid = graphene.List(graphene.String)  # ...(description='A typical hello world')
    seq = graphene.List(graphene.String)


class Taxon(graphene.ObjectType):
    uid = graphene.String()
    name = graphene.String()
    parent = graphene.String()
    children = graphene.List(graphene.Int)
    # sequence = graphene.Field(  # InputFields
    #     Sequence,
    #     uid=graphene.List(graphene.String),
    #     max=graphene.Int(default_value=10),
    #     resolver=resolve_sequence)  # https://github.com/graphql-python/graphene/issues/221
    # sequence = graphene.Field(lambda: Sequence)
    # http://docs.graphene-python.org/en/latest/execution/dataloader/