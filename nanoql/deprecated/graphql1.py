'''
The resolver usually sits in the server. But since we wrap the REST API to prove a
point, we "cheat" and put the resolver on the client side. But this explains, why
the resolver will not return implicit objects, bc/ it is meant to send JSON.

tiers in ENA

- reads
- assembly
- annotation

https://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.Application_4_Finding_unique_se
https://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EPost_
https://www.ncbi.nlm.nih.gov/books/NBK25497/

examples: https://github.com/graphql-python/swapi-graphene
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
    from nanoql.objects import Sequence, InputSequence, Taxon
    from nanoql.resolver import resolve_sequence, resolve_taxon
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
    taxon = graphene.Field(Taxon,
        uid=graphene.String(),
        name=graphene.String(),
        sequence=InputSequence(),
        resolver=resolve_taxon)


schema = graphene.Schema(query=Query)

params = {'keys': ["KC790375", "KC790376", "KC790377", "KC790378"]}
query = '''
    query ($keys: [String]) {
      sequence(uid: $keys, max: 3) {
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
# another use case: get pseudomonas pangenome
# another: all influenza data for deep learning

schema = graphene.Schema(query=Query)
query = '''
    query {
      taxon(name: "pseudomonas aeruginosa") {
        taxid
        name
        parent
        children
      }
    }
'''
e = schema.execute(query, context_value={'db': 'genbank'})
e.data, e.errors, e.invalid


# ------------------------------------------------------------------------------
# Below does not work.

# Maybe first should be resolve gff file an get e.g. only annotation.


schema = graphene.Schema(query=Query)
query = '''
    query {
      taxon(name: "pseudomonas aeruginosa") {
        taxid
        name
        parent
        children {
          taxid
          sequence {  # resolver should return sequence object?
            seq
            host
          }
        }
      }
    }
'''
e = schema.execute(query, context_value={'db': 'genbank'})
e.data, e.errors, e.invalid
# graphql.error.base.GraphQLError('Cannot query field "sequence" on type "Taxon".')


'''
"Note that Input and Output data have different types by design (as reflected in the GraphQL spec), so you can't use a ObjectType as input."
- https://github.com/graphql-python/graphene/issues/431
- therein mentioned playground example

basically, we have to get tax info from query and separately seq info using the same
query (like pseudomonas aeruginosa), then the two canbe "joined" in the query
'''





# TODO: pass one argument to the next nesting
query = '''
    query {
      taxon(name: "pseudomonas aeruginosa") {
        name
        parent
          sequence {  # uid gets inferred from parent ID?
              uid
              seq
        }
        assembly(...) {
        ...
        }
      }
    }
'''

# here parent basically mimicks query

# https://stackoverflow.com/questions/39732223/graphql-pass-args-to-sub-resolve
# https://stackoverflow.com/questions/44159753/java-graphql-pass-field-values-to-resolver-for-objects

'''
An AbstractType contains fields that can be shared among graphene.ObjectType,
graphene.Interface, graphene.InputObjectType or other graphene.AbstractType.
-- http://docs.graphene-python.org/en/latest/types/abstracttypes/

InputFields are used in mutations to allow nested input data for mutations
-- http://docs.graphene-python.org/en/latest/types/mutations/

{
  me {
    name
    bestFriend {
      name
    }
    friends(first: 5) {
      name
      bestFriend {
        name
      }
    }
  }
}

http://docs.graphene-python.org/en/latest/execution/dataloader/



https://github.com/graphql-python/graphene/tree/master/graphene/types/tests

"How to access arguments from higher levels"
https://github.com/graphql-python/graphene/issues/378

"How to access parent field parameters within child resolver"
https://github.com/graphql-python/graphene/issues/510

lambda
https://github.com/graphql-python/graphene/issues/461

json
https://github.com/graphql-python/graphene/issues/384

self, root -- difference?
https://github.com/graphql-python/graphene/issues/278
'''