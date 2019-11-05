aliases = ['r']

def generate(args):
    if len(args) != 1:
        msg = 'The field type "range" takes a single argument. i.e., a range descriptor'
        raise ValueError(msg)
    # ---
    vals = args[0].split(',')
    vals = [int(v) for v in vals]
    if len(vals) == 1:
        return range(vals[0])
    elif len(vals) == 2:
        return range(vals[0], vals[1], 1)
    elif len(vals) == 3:
        return range(vals[0], vals[1], vals[2])
    else:
        msg = 'The argument for field type "range" can be of the forms:' + \
                '   - f  ->  [0,1,...,f)' + \
                '   - s,f  ->  [s,s+1,...,f)' + \
                '   - s,f,i  ->  [s,s+i,...,f)'
        raise ValueError(msg)
