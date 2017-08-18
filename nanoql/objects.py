import graphene

class Sequence(graphene.ObjectType):
    uid = graphene.List(graphene.String)  # ...(description='A typical hello world')
    seq = graphene.List(graphene.String)