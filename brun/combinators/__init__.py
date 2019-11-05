from .cross import combine as combine_cross
from .zip import combine as combine_zip
from .zipl import combine as combine_zipl

_combinator_map = {
    'default': combine_cross,
    'cross': combine_cross,
    'zip': combine_zip,
    'zipl': combine_zipl,
}

def _get_combinator(comb_name):
    if not comb_name in _combinator_map:
        msg = f'Grouping strategy "{comb_name}" not found!'
        raise ValueError(msg)
    # ---
    return _combinator_map[comb_name]
