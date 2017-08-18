import json
import graphene
import requests
from nanoql.graphql import Query


def test_taxon():
    schema = graphene.Schema(query=Query)
    query = '''
        query {
            taxon(name: "pseudomonas aeruginosa") {
                uid
                name
                parent
                children
            }
        }
        '''
    e = schema.execute(query, context_value={'db': 'genbank'})
    if not e.invalid:
        assert e.data['taxon']['uid'] == '287'


def test_sequence():
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
    if not e.invalid:
        assert len(e.data['sequence']['seq']) == 3
        assert e.data['sequence']['seq'][2] == 'ATGGGGAACA'
