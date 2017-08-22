DO NOT USE YET, WORK IN PROGRESS (2017-08-18).

## nanoql

NCBI sucks. ENA is better, but is still enoying and sparsely documented. That's where nanoql comes in. It is a domain-specific (mini) language to query these databases based on the GraphQL API spec.

The ["why"](https://www.youtube.com/watch?v=ND9GWSkbUGM) of GraphQL.

```
query(db: "ena", uid: 12345) {
    info {
        host
        geo
        datetime
    }
    assembly {
        sequence
    }
    annotation {
        cds
    }
}
```

### Live demo

```bash
pip install flask
pip install flask_graphql

python ~/repos/nanoql/nanoql/app.py
# direct browser to http://localhost:5000/graphql
```

make sure no file in the nanoql/nanoql folder is named "graphql.py", see [here](https://github.com/graphql-python/graphene-django/issues/108)

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
