import time
import os
import numpy as np
from joblib import Parallel, delayed, dump, load


def slow_mean(data, sl):
    """Simulate a time consuming processing."""
    time.sleep(0.01)
    return data[sl].mean()


def slow_mean_write_output(data, sl, output, idx):
    """Simulate a time consuming processing."""
    time.sleep(0.005)
    res_ = data[sl].mean()
    #print("[Worker %d] Mean for slice %d is %f" % (os.getpid(), idx, res_))
    output[idx] = res_


def main1():
    """main"""
    data = np.random.random((int(1e7),))
    window_size = int(5e5)
    slices = [slice(start, start + window_size)
              for start in range(0, data.size - window_size, int(1e5))]
    start = time.time()
    results1 = [slow_mean(data, sl) for sl in slices]
    print('Elapsed time computing the average of couple of slices:', time.time()-start)
    print(results1, '\n')

    start = time.time()
    results2 = Parallel(n_jobs=4)(delayed(slow_mean)(data, sl) for sl in slices)
    print('Elapsed time computing the average of couple of slices:', time.time()-start)
    print(results2, '\n')

    folder = './joblib_memmap'
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

    data_filename_memmap = os.path.join(folder, 'data_memmap')
    dump(data, data_filename_memmap)
    data2 = load(data_filename_memmap, mmap_mode='r')

    start = time.time()
    results3 = Parallel(n_jobs=4)(delayed(slow_mean)(data2, sl) for sl in slices)
    print('Elapsed time computing the average of couple of slices:', time.time()-start)
    print(results3, '\n')

    output_filename_memmap = os.path.join(folder, 'output_memmap')
    output = np.memmap(output_filename_memmap, dtype=data.dtype, shape=len(slices), mode='w+')
    Parallel(n_jobs=4)(delayed(slow_mean_write_output)(data2, sl, output, idx) for idx, sl in enumerate(slices))
    print('output = ', output)


def main2():
    """main"""
    data = np.random.random((int(1e7),))
    print(data[0])
    window_size = int(5e5)
    slices = [slice(start, start + window_size)
              for start in range(0, data.size - window_size, int(1e5))]
    results = [slow_mean(data, sl) for sl in slices]
    print(results, '\n')

    folder = './joblib_memmap'
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

    data_filename_memmap = os.path.join(folder, 'data_memmap')
    dump(data, data_filename_memmap)
    data2 = load(data_filename_memmap, mmap_mode='r')
    print(type(data2))
    output_filename_memmap = os.path.join(folder, 'output_memmap')
    output = np.memmap(output_filename_memmap, dtype=data.dtype, shape=len(slices), mode='w+')
    Parallel(n_jobs=4)(delayed(slow_mean_write_output)(data2, sl, output, idx) for idx, sl in enumerate(slices))
    print("\nActual means computed by the worker processes:\n {}".format(output[0]))
    print(type(output))


if __name__ == '__main__':
    #main1()
    main2()
