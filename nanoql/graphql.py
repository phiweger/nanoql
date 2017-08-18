'''
The resolver usually sits in the server. But since we wrap the REST API to prove a
point, we "cheat" and put the resolver on the client side. But this explains, why
the resolver will not return implicit objects, bc/ it is meant to send JSON.
'''

# TODO: http://docs.graphene-python.org/en/latest/execution/dataloader/
# TODO: http://docs.graphene-python.org/en/latest/types/mutations/


import json
import graphene
import requests
# https://github.com/graphql-python/graphene/blob/master/examples/simple_example.py
# try live: http://graphene-python.org/playground/
# info:
# - http://nafiulis.me/graphql-in-the-python-world.html


class Query(graphene.ObjectType):
    from nanoql.objects import Sequence
    from nanoql.resolver import resolve_sequence
    #  GraphQL fields are designed to be stand-alone functions. --
    # http://docs.graphene-python.org/en/latest/execution/dataloader/
    sequence = graphene.Field(
        Sequence,
        # uid=graphene.Argument(
        #     graphene.String,
        #     default_value='pseudomonas aeruginosa')
        mock=graphene.String(default_value='pseudomonas aeruginosa'),
        uid=graphene.List(graphene.String),
        max=graphene.Int(default_value=10),
        # see "Types mounted in a Field act as Arguments."
        # -- http://docs.graphene-python.org/en/latest/types/scalars/
        resolver=resolve_sequence)
    # The uid of a field's args has to be passed to the field constructer, see
    # stackoverflow, 42142046.
    # Alternatively, pass an graphene.InputObjectType, like GeoInput() here:
    # https://github.com/graphql-python/graphene/blob/master/examples/complex_example.py


schema = graphene.Schema(query=Query)
params = {'keys': ["KC790375", "KC790376", "KC790377", "KC790378"]}

query = '''
    query ($keys: [String]) {
      sequence(uid: $keys, max: 5) {
        uid
        seq
      }
    }
'''
e = schema.execute(query, variable_values=params, context_value={'db': 'genbank'})
# Lists work in a similar way: We can use a type modifier to mark a type as a List,
# which indicates that this field will return an array of that type. In the schema
# language, this is denoted by wrapping the type in square brackets, [ and ]. It works
# the same for arguments, where the validation step will expect an array for that value.
# -- http://graphql.org/learn/schema/
e.data, e.errors, e.invalid
print(json.dumps(dict(e.data['sequence']), indent=2))

# get all the data from: http://www.nature.com/nature/journal/v540/n7634/full/nature20167.html#accessions
# as a nice use case
# another use case: get



- reads
- assembly
- annotation