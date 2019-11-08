aliases = ['r']

def generate(args):
    if len(args) != 1:
        msg = 'The field type "range" takes a single argument. i.e., a range descriptor'
        raise ValueError(msg)
    # ---
    vals_str = args[0].split(',')
    vals = [int(v) for v in vals_str]
    fmt = _extract_format(vals_str)
    if len(vals) == 1:
        return _format(range(vals[0]), fmt)
    elif len(vals) == 2:
        return _format(range(vals[0], vals[1], 1), fmt)
    elif len(vals) == 3:
        return _format(range(vals[0], vals[1], vals[2]), fmt)
    else:
        msg = 'The argument for field type "range" can be of the forms:' + \
                '   - f  ->  [0,1,...,f)' + \
                '   - s,f  ->  [s,s+1,...,f)' + \
                '   - s,f,i  ->  [s,s+i,...,f)'
        raise ValueError(msg)


def _extract_format(vals_str):
    args = vals_str + [vals_str[0]]
    s, f = (args[0], args[1]) if int(args[1]) > int(args[0]) else (args[1], args[0])
    if len(s) != len(str(int(s))):
        padding_len = len(s) - len(str(int(s)))
        padding = s[:padding_len]
        if len(set(padding)) != 1:
            msg = 'Formatted arguments in field "range" must have a single char padding'
            raise ValueError(msg)
        padding_char = padding[0]
        return "{:%s%sd}" % (padding_char, len(s))
    return "{0}"

def _format(lst, fmt):
    return list(map(lambda v: fmt.format(v), lst))
