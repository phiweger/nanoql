import time
import warnings
warnings.filterwarnings('ignore')  # does not suppress messages
# https://stackoverflow.com/questions/14463277/how-to-disable-python-warnings

# WARNING:curio.task:Task(id=868, name='worker',
# <coroutine object worker at 0x1112e90a0>, state='TERMINATED') never joined
# https://github.com/dabeaz/curio/issues/212

import curio
import asks
# We could use grequests or a similar solution. However, async is the future,
# so let's invest in it.
# - https://github.com/ross/requests-futures
# - grequests
asks.init('curio')


def chunks(l, n):
    '''
    Yield successive n-sized chunks from l (stackoverflow, 312443).
    a = [1, 2, 3, 4]
    list(chunks(a, 2))
    # [[1, 2], [3, 4]]
    Returns empty list if list empty.
    For overlapping chunks, see windows()
    '''
    for i in range(0, len(l), n):
        yield l[i:i + n]


uid_list = []
for i in range(24):
    uid_list.append('AEVV030000' + '{:02d}'.format(i))
    # https://stackoverflow.com/questions/339007/nicest-way-to-pad-zeroes-to-string

url_list = []
base = 'http://www.ebi.ac.uk/ena/data/view/'
for uid in uid_list:
    url_list.append(base + uid + '&display=fasta')


# see http://asks.readthedocs.io/en/latest/idioms.html
# Sanely making many requests (with semaphores)
# TODO: Handling response body content (downloads etc.)


results = []


async def worker(sema, url):
    async with sema:
        r = await asks.get(url)
        print('foo')
        results.append(r)
        print('got ', url)
        # with open('/tmp/foo.fa', 'a+') as out_file:
        #     out_file.write(r.text[:140] + '\n')  # this seems to be blocking


async def main(url_list):
    sema = curio.BoundedSemaphore(value=8) # Set sofa size.
    async with curio.TaskGroup() as g:
        # TaskGroup deals with warning:
        # Task(id=187, name='worker', <coroutine object worker at 0x1111f85c8>, state='TERMINATED') never joined
        # http://curio.readthedocs.io/en/latest/reference.html#task-groups
        # https://github.com/dabeaz/curio/issues/212#issuecomment-325589080
        # problem: if one task fails, all fail
        for chunk in chunks(url_list, 2):
            for url in chunk:
                await g.spawn(worker(sema, url))  # t tasks
                print('bar')
                # await t.join()  # this would make things synchronous

tic = time.time()
curio.run(main(url_list))
toc = time.time()  # 2.45 s (8 virtual cores), even faster than map_async() below

tic = time.time()
[requests.get(i) for i in url_list]
toc = time.time()  # 17.52 s


# alternative way (easier I think) to do it, see
# https://github.com/kblin/ncbi-genome-download/blob/master/ncbi_genome_download/core.py
'''
        pool = Pool(processes=parallel)
        jobs = pool.map_async(worker, download_jobs)
        try:
            # 0xFFFF is just 'a really long time'
            jobs.get(0xFFFF)
        except KeyboardInterrupt:  # pragma: no cover
            # TODO: Actually test this once I figure out how to do this in py.test
            logging.error('Interrupted by user')
            return 1
'''


from multiprocessing import Pool, pool, cpu_count
import sys
import time

import click
import requests


# source:
# https://github.com/kblin/ncbi-genome-download/blob/master/ncbi_genome_download/core.py
# support Aspera?
# https://github.com/kblin/ncbi-genome-download/issues/15
# https://github.com/kblin/ncbi-genome-download/issues/46


# All the logic of how to get file and what to do with it goes into the worker.
def worker(url, fp='/tmp/bar.fa'):
    '''Run a single download job'''
    try:
        if url is not None:
            result = requests.get(url, stream=True)

            # TODO: adjust number of points for items in request
            print('.', file=sys.stderr, end='')
            sys.stderr.flush()
            with open(fp, 'a+') as out:
                out.write(result.text[:150] + '\n')
            # TODO: check result
    except KeyboardInterrupt:  # pragma: no cover
        # TODO: Actually test this once I figure out how to do this in py.test
        logging.debug('Ignoring keyboard interrupt.')
        return 1
    return result


def gather(nproc=cpu_count()):
    # Actual logic
    try:
        pool = Pool(processes=nproc)
        tasks = pool.map_async(worker, url_list)
        print('Downloading files, one dot at a time:', file=sys.stderr)
        sys.stderr.flush()
        try:
            # 0xFFFF is just 'a really long time'
            tasks.get(0xFFFF)
            print('\nDone.', file=sys.stderr)
            sys.stderr.flush()
        except KeyboardInterrupt:  # pragma: no cover
            # TODO: Actually test this once I figure out how to do this in py.test
            logging.error('Interrupted by user')
            return 1

    except requests.exceptions.ConnectionError as err:
        logging.error('Download from NCBI failed: %r', err)
        # Exit code 75 meas TEMPFAIL in C/C++, so let's stick with that for now.
        return 75
    return 0


tic = time.time()
gather()  # will use 4 cores
toc = time.time()  # takes about the same time as the curio solution
toc - tic

'''
some inconsistencies to take into account

>ENA|AEVV03000000|AEVV03000000.3 null

>ENA|AEVV03000007|AEVV03000007.1 Pseudomonas aeruginosa HB13 strain 138244 contig000007, whole genome shotgun sequence.
GCCCCTCTATTGAGAGCGCATTCCTGCCC
AEVV03000015 has been suppressed at the submitter's request on 2016-11-30 12:02:21.0

>ENA|AEVV03000016|AEVV03000016.1 Pseudomonas aeruginosa HB13 strain 138244 contig000016, whole genome shotgun sequence.
CGCTGCACGGTGAGGCGCAGGCCGCTGTC
'''
