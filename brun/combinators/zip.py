from brun import brlogger


def combine(lst1, lst2, _):
    if len(lst1) != len(lst2):
        brlogger.warning('Zipping two sets of different sizes {} != {}'.format(
            len(lst1), len(lst2)))
    return zip(lst1, lst2)
