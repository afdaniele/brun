import os
import types

class IterableNamespace(types.SimpleNamespace):

    # forward iterator to internal dict
    def __iter__(self):
        return self.__dict__.__iter__()



def stringify(lst):
    return list(map(str, lst))


def get_sandbox(sbox_id):
    unit_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join(unit_dir, 'sandbox', 's{}'.format(sbox_id)))

def get_sandbox_object(sbox_id, uri):
    return os.path.abspath(os.path.join(get_sandbox(sbox_id), uri))
