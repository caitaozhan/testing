def gen_cat(sources):
    '''concatenate items from one or more source into a single sequences of items
    '''
    for src in sources:
        yield from src
