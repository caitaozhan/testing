''' a python version of tail -f
'''

import time
import os

def follow(thefile):
    thefile.seek(0, os.SEEK_END) # End-of-file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1) # Sleep briefly
            continue
        yield line


if __name__ == '__main__':
    logfile = open('access-log')
    loglines = follow(logfile)

    for line in loglines:
        print(line, end='')
