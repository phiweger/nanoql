WORK IN PROGRESS (2017-08-25).

## nanoql

NCBI sucks. ENA is better, but is still ennoying and sparsely documented. That's where nanoql comes in. It is a domain-specific (mini) language. It is used to query multiple databases based on the [GraphQL API](https://en.wikipedia.org/wiki/GraphQL) spec that Facebook open sourced in 2015.

The ["why"](https://www.youtube.com/watch?v=ND9GWSkbUGM) of GraphQL:

- only get the data you want (not too little and not too much)
- no knowledge about the internal (dis)organisation of the database you query against (e.g. the ENA's REST API)
- one endpoint to query multiple databases with the same syntax
- if changes occur to the databases' schemas, the queries you do stay syntactically the same
- if new fields are added to nanoql's API, the old queries are still valid

Example queries:

```
{
  taxon(key: "Pseudomonas aeruginosa", n_children: 4) {
    taxid
    name
    lineage {
      family
      order
      cls
      phylum
    }
    children {
      name
      taxid
    }
  }
}
```

This query returns a nice JSON record:

```
{
  "data": {
    "taxon": [
      {
        "taxid": "287",
        "name": "Pseudomonas aeruginosa",
        "lineage": {
          "family": "Pseudomonadaceae",
          "order": "Pseudomonadales",
          "cls": "Gammaproteobacteria",
          "phylum": "Proteobacteria"
        },
        "children": [
          {
            "name": "Pseudomonas aeruginosa 2192",
            "taxid": "350703"
          },
          {
            "name": "Pseudomonas aeruginosa PA14",
            "taxid": "652611"
          },
          {
            "name": "Pseudomonas aeruginosa C-NN2",
            "taxid": "910265"
          },
          {
            "name": "Pseudomonas aeruginosa NCAIM B.001380",
            "taxid": "1118159"
          }
        ]
      }
    ]
  }
}
```

Try these queries if you like:

```
{
  taxon(key: 287) {
    stats
  }
}


# nice error messages
{
  taxon(key: 278) {
    stats
  }
}
```

### Live demo

```bash
pip install nanoql, flask, flask_graphql
python path/to/repo/nanoql/nanoql/app.py
# direct your browser to http://localhost:5000/graphql and explore
```

### Install

tested Python3.6

```
pip install nanoql
```

### Testing

nanoql adheres to pytest's package integration [guidance](http://doc.pytest.org/en/latest/goodpractices.html).

```shell
# cd into package directory and virtualenv (Python 3)
python setup.py test

# test Python 2.7 and 3.5
tox  # not yet
```

### Licence

BSD-3-Clause

Copyright (c) 2017 Adrian Viehweger
