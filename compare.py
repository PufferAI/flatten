import numpy as np
from collections import OrderedDict


def compare_arrays(array_1, array_2):
    assert isinstance(array_1, np.ndarray)
    assert isinstance(array_2, np.ndarray)
    assert array_1.shape == array_2.shape
    return np.allclose(array_1, array_2)

def compare_dicts(dict_1, dict_2):
    assert isinstance(dict_1, (dict, OrderedDict))
    assert isinstance(dict_2, (dict, OrderedDict))

    if not all(k in dict_2 for k in dict_1):
        raise ValueError("Keys do not match between dictionaries.")

    for k, v in dict_1.items():
        if not compare(v, dict_2[k]):
            return False

    return True

def compare_lists(list_1, list_2):
    assert isinstance(list_1, (list, tuple))
    assert isinstance(list_2, (list, tuple))

    if len(list_1) != len(list_2):
        raise ValueError("Lengths do not match between lists/tuples.")

    for v1, v2 in zip(list_1, list_2):
        if not compare(v1, v2):
            return False
        
    return True
    
def compare(data_1, data_2):
    '''Compare two samples from the same space
    
    Optionally, sample_2 may be a batch of samples from the same space
    concatenated along the first dimension of the leaves. In this case,
    sample_2_batch_idx specifies which sample to compare.
    '''
    if isinstance(data_1, (dict, OrderedDict)):
        return compare_dicts(data_1, data_2)
    elif isinstance(data_1, (list, tuple)):
        return compare_lists(data_1, data_2)
    elif isinstance(data_1, np.ndarray):
        assert isinstance(data_2, np.ndarray)
        return compare_arrays(data_1, data_2)
    elif isinstance(data_1, (int, float)):
        if isinstance(data_2, np.ndarray):
            assert data_2.size == 1, "Cannot compare scalar to non-scalar."
            data_2 = data_2[0]
        return data_1 == data_2
    else:
        return data_1 == data_2