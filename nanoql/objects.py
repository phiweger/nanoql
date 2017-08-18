import graphene

class Sequence(graphene.ObjectType):
    uid = graphene.List(graphene.String)  # ...(description='A typical hello world')
    seq = graphene.List(graphene.String)

class Taxon(graphene.ObjectType):
    uid = graphene.String()
    name = graphene.String()
    # parent = graphene.String()
    # children = graphene.List(graphene.String)