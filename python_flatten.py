from pdb import set_trace as T
import warnings

from numba import jit

DICT = 0
LIST = 1
TUPLE = 2
VALUE = 3


def flatten_structure(data):
    structure = []
    
    def helper(d):
        if isinstance(d, dict):
            structure.append(DICT)
            structure.append(len(d))
            for key, value in d.items():
                structure.append(key)
                helper(value)
        elif isinstance(d, list):
            structure.append(LIST)
            structure.append(len(d))
            for item in d:
                helper(item)
        elif isinstance(d, tuple):
            structure.append(TUPLE)
            structure.append(len(d))
            for item in d:
                helper(item)
        else:
            structure.append(VALUE)
    
    helper(data)
    return structure

def naive_flatten(data):
    flat_data = []
    
    def helper(d):
        if isinstance(d, dict):
            for key, value in d.items():
                helper(value)
        elif isinstance(d, (list, tuple)):
            for item in d:
                helper(item)
        else:
            flat_data.append(d)
    
    helper(data)
    return flat_data

def flatten(data):
    flat_data = []
    stack = [data]
    while stack:
        d = stack.pop()
        if isinstance(d, dict):
            for key, value in d.items():
                stack.append(value)
        elif isinstance(d, (list, tuple)):
            for item in d:
                stack.append(item)
        else:
            flat_data.append(d)

    return flat_data[::-1]

@jit
def numba_flatten(data):
    flat_data = []
    stack = [data]
    while stack:
        d = stack.pop()
        if isinstance(d, dict):
            for key, value in d.items():
                stack.append(value)
        elif isinstance(d, (list, tuple)):
            for item in d:
                stack.append(item)
        else:
            flat_data.append(d)

    return flat_data[::-1]

def unflatten(flat_data, structure):
    return unflatten_helper(flat_data, structure, 0, 0)[0]

def unflatten_helper(flat_data, structure, struct_idx, data_idx):
    token = structure[struct_idx]

    struct_idx += 1 
    if token == DICT:
        n = structure[struct_idx]
        struct_idx += 1 
        result = {}
        for _ in range(n):
            key = structure[struct_idx]
            struct_idx += 1
            value, struct_idx, data_idx = unflatten_helper(flat_data, structure, struct_idx, data_idx)
            result[key] = value
        return result, struct_idx, data_idx
    elif token == LIST:
        n = structure[struct_idx]
        struct_idx += 1 
        result = []
        for _ in range(n):
            value, struct_idx, data_idx = unflatten_helper(flat_data, structure, struct_idx, data_idx)
            result.append(value)
        return result, struct_idx, data_idx
    elif token == TUPLE:
        n = structure[struct_idx]
        struct_idx += 1 
        result = []
        for _ in range(n):
            value, struct_idx, data_idx = unflatten_helper(flat_data, structure, struct_idx, data_idx)
            result.append(value)
        return tuple(result), struct_idx, data_idx
    else:
        result = flat_data[data_idx]
        data_idx += 1
        return result, struct_idx, data_idx