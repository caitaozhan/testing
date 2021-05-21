import gzip, bz2
from pathlib import Path
from gencat import gen_cat

def gen_open(paths):
    '''takes a sequence of paths as input and yields a sequence of open file objects
    '''
    for path in paths:
        if path.suffix == '.gz':
            yield gzip.open(path, 'rt')
        elif path.suffix == '.bz2':
            yield bz2.open(path, 'rt')
        else:
            yield open(path, 'rt')


if __name__ == '__main__':
    lognames = Path('./').rglob("access-log*")
    logfiles = gen_open(lognames)
    loglines = gen_cat(logfiles)
    for line in loglines:
        print(line)
