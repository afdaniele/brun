import itertools

def combine(lst1, lst2, args):
    if len(args) != 1:
        msg = 'The grouping strategy "zipl" requires a fill argument'
        raise ValueError(msg)
    fill = args[0]
    return itertools.zip_longest(lst1, lst2, fillvalue=fill)
