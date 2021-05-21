'''http://www.dabeaz.com/generators/Generators.pdf
   page 101
'''

import threading, queue
from genqueue import genfrom_queue, sendto_queue
from gencat import gen_cat
from yield_threadsafe2 import simple_generator, thread_safe_generator


def multiplex(sources):
    in_q = queue.Queue()
    consumers = []
    for src in sources:
        t = threading.Thread(target=sendto_queue, args=(src, in_q))
        t.start()
        consumers.append(genfrom_queue(in_q))
    return gen_cat(consumers)



if __name__ == '__main__':
    gens = []
    for i in range(3):
        gen = thread_safe_generator(simple_generator(i))
        # gen = simple_generator(i)
        gens.append(gen)

    multi = multiplex(gens)
    for i in multi:
        print(i)
