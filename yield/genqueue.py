'''generators and threads
http://www.dabeaz.com/generators/Generators.pdf  -- page 89
'''

from follow import follow


def sendto_queue(source, thequeue):
    '''feed a generated sequece into a queue
    '''
    for item in source:
        thequeue.put(item)
    thequeue.put(StopIteration)


def genfrom_queue(thequeue):
    while True:
        item = thequeue.get()
        if item is StopIteration:
            break
        yield item


