# TODO make ENA version of this, NCBI should be only fallback
def fetch_uid(uid=None, name='', context=None, max_n_records=None):
    '''Fetch sequence data from <context>.

    max_n_records .. None means all

    Example:

    result = fetch_uid(uid=['KC790373', 'KC790374'], context='ncbi')
    '''

    import requests

    if context == 'ncbi':
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        params = {
            'db': 'nuccore',
            'id': uid,  # 'KC790373'
            'rettype': 'fasta',
            'retmode': 'text',
            'retmax': max_n_records}  # if arg is None, requests wont include it
        result = requests.get(url, params)
        return result
    else:
        raise ValueError('Not yet implemented.')


def fmt_fasta(result):
    '''Format the requests result.

    Example:

    from nanohq.restapi import fetch_uid, fmt_fasta

    result = fetch_uid(uid=['KC790373', 'KC790374'], context='ncbi')
    a = fmt_fasta(result)
    next(a)  # ('KC790373.1', 'ATGGGGAACA')
    '''
    from io import StringIO
    from Bio import SeqIO

    for read_ in SeqIO.parse(StringIO(result.text), format='fasta'):
        # read_ as to not override builtin read()
        yield read_.description.split(' ')[0], str(read_.seq)[:20]