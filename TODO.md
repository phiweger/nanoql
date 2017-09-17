## TODO

don't "look" at the sequence, it's usually of no interest, we just want to download it

application:

- get synonyms for "semliki forest"
- select appropriate name and get id of all complete sequences
- download them to fasta and bed

two stwp process: explore with Graphiql, once satisfied copy query into file and
fetch data

```python
nanoql explore --port 5000  # starts server
nanoql fetch --query search.ql --out /path/to/... --fmt fasta --parallel 8
# get data, i.e. sequences, in e.g. fasta format
```
