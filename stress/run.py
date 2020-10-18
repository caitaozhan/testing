'''
stress a single core
'''
import numpy as np
import time

if __name__ == '__main__':
    stop = int(1e7)
    start = time.time()
    for i in range(stop):            # time of one iteration is 0.004 millisecond or 4 microseconds
        a = np.random.rand(10, 10)
        b = np.random.rand(10, 10)
        c = a@b
    print('time {:.2f}s'.format(time.time() - start))
