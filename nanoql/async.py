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
        with open('/tmp/foo.fa', 'a+') as out_file:
            out_file.write(r.text[:140] + '\n')  # this seems to be blocking


async def main(url_list):
    sema = curio.BoundedSemaphore(value=8) # Set sofa size.
    for chunk in chunks(url_list, 2):
        for url in chunk:
            await curio.spawn(worker(sema, url))
            print('bar')
            # await t.join()  # this would make things synchronous

# TODO:
# deal with warning:
# Task(id=187, name='worker', <coroutine object worker at 0x1111f85c8>, state='TERMINATED') never joined
# join? http://curio.readthedocs.io/en/latest/tutorial.html

tic = time.time()
curio.run(main(url_list))
toc = time.time()  # 2.45 s (8 virtual cores)

tic = time.time()
[requests.get(i) for i in url_list]
toc = time.time()  # 17.52 s