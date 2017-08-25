'''
Use case: Given a list of accession ids, get both taxonomic info and sequence info from it. Sequence can be raw reads, assembly (curation level 1) or annotation (curation level 2).

https://stackoverflow.com/questions/39381436/graphql-django-resolve-queries-using-raw-postgresql-query

https://github.com/graphql-python/graphene/issues/462
https://github.com/graphql-python/graphene/issues/431
'''

import json
import graphene
from graphene import InputObjectType, ObjectType, String, ID, Field, List
# from graphene.types.json import JSONString


# https://gist.github.com/href/1319371
def convert_to_obj(dictionary, name='GenericDict'):
    from collections import namedtuple
    NT = namedtuple(name, dictionary.keys())
    gen_dict = NT(**dictionary)
    return gen_dict


class Sequence(ObjectType):
    '''Gets passed a dict (from e.g. InputSequence object).'''
    seqid = ID(description='foo', required=False, default_value=None)
    # params: description, default, required
    seq = List(String)

    def resolve_seqid(self, args, context, info):
        return int(self.get('seqid')[-1]) + 1

    def resolve_seq(self, args, context, info):
        from nanoql.restapi import fetch_uid, fmt_fasta

        result = fetch_uid(uid=self.get('seqid'), context='ncbi')
        header, seq = next(fmt_fasta(result))
        return ['fasta', header + '\n' + seq + '\n']  # problem: this is a string


# https://github.com/graphql-python/graphene/issues/431
# see playground link therein
class InputSequence(InputObjectType):
    # define the fields this input sequence
    seqid = ID()
    seq = String()


class Info(ObjectType):
    taxid = ID()
    name = String()
    parent = ID()
    children = List(ID)


class Taxon(ObjectType):
    info = Field(Info)
    taxid = ID()
    name = String()
    sequence = Field(Sequence)

    def resolve_taxid(self, args, context, info):
        return self.get('name')  # taxid field gets name

    def resolve_name(self, args, context, info):
        return self['taxid']  # name field gets taxid, note syntax

    def resolve_info(self, args, context, info):
        from nanoql.restapi import fetch_taxname, fmt_taxon

        result = next(fmt_taxon(fetch_taxname(self.get('name'))))
        info = convert_to_obj(result, name='Info')
        return info

    def resolve_sequence(self, args, context, info):
        return self.get('sequence')


def resolve_sequence(self, args, context, info):
    return [dict(seqid=k) for k in args['seqid']]


def resolve_taxon(self, args, context, info):
    # to return multiple results, just return them
    return [dict(taxid=k, name=args['name'], sequence={"seqid": k, "seq": "ACTG"})
        # in the query this could be
        # taxon(sequence: {seqid: K3232, ...})
        # i.e. we could pass this directly via InputSequence object
        # note also how to pass a param from taxon down to sequence (k)
            for k in args['taxid']]


class Query(ObjectType):
    taxon = List(  # why not Field? because returns list?
        Taxon,
        taxid=List(ID),
        name=String(),
        info=String(),  #  Field(Info) ########################
        sequence=InputSequence(),
        resolver=resolve_taxon
    )

    sequence = List(
        Sequence,
        seqid = List(ID),
        seq = String(),  # this is the reason a string is returned from Sequence object
        resolver=resolve_sequence
    )


schema = graphene.Schema(query=Query)


# Aim: For a list of IDs, get the taxon info as well as the sequencing info.
params = {'key': ["KC790375", "KC790376", "KC790377"]}
query = '''
query($key: [ID]) {
  taxon(taxid: $key, ) {
    taxid
    name
    sequence {
      seqid
      seq
    }
  }
}
'''

# e = schema.execute(query, variable_values=params)
# e.data, e.errors, e.invalid
# print(json.dumps(e.data, indent=2))


# query = '''
# query {
#   sequence(seq: "ACTG", seqid: "KC790375") {
#     seqid
#     seq
#     }
# }
# '''
#
# e = schema.execute(query)
# e.data, e.errors, e.invalid


'''
query{
  sequence(seqid: ["KC750375", "KC750376"]){
    seq
    seqid
  }
}

query {
  taxon(taxid: ["KC750375", "KC750377"]) {
    taxid
    name
    sequence {
      seqid
      seq
    }
  }
}

query {
  taxon(taxid: [286, 287], name:"pseudomonas aeruginosa") {
    name
  }
}

query {
  taxon(taxid: [287, 288], name: "pseudomonas aeruginosa") {
    taxid
    name {
      parent
      children
    }
    sequence {
      seqid
    }
  }
}
'''