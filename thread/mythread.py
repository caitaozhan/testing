'''
Thread learning: https://realpython.com/intro-to-python-threading/
'''

import logging
import threading
import time
import random

def thread_function(name, sec):
    logging.info('Thread {} starting'.format(name))
    for i in range(sec):
        time.sleep(1)
        print('Thread {} - {}'.format(name, i))
    logging.info('Thread {} finished'.format(name))


class foo:
    '''an instance method can be the target of a thread
    '''
    def __init__(self):
        pass

    def function(self, number):
        print('enter the thread')
        for i in range(number):
            time.sleep(random.random())
            print(f'{i}/{number}')
        print('exit the thread')

    def run(self):
        threads = []
        for i in range(4, 6):
            threads.append(threading.Thread(target=self.function, args=(i,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

def main1():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main   : before creating thread")
    x = threading.Thread(target=thread_function, args=(1,3), daemon=True)
    y = threading.Thread(target=thread_function, args=(2,5), daemon=True)
    logging.info("Main   : before running thread")
    x.start()
    y.start()
    logging.info("Main   : wait for the thread to finish")
    x.join()
    y.join()
    logging.info("Main   : all done")

def main2():
    f = foo()
    f.run()

if __name__ == '__main__':
    # main1()
    main2()