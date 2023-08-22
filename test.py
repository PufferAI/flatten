from pdb import set_trace as T

import numpy as np
import timeit

from compare import compare

import python_flatten
import cython_flatten
import c_flatten
import rust_flatten

# The two commented cases break C
test_cases = [
    [1, {'foo': (2, 'a')}, (5, 3)],
    #{'a': (1, [3, 4]), 'b': {'c': [[5, 6], 7, [8, 4]], 'd': 3}, 'e': 5},
    [[True, False], {'x': 3.14, 'y': 2.71}, ('hello', 'world')],
    #{1: 'one', 2: [3, 4], 3: {'a': (5, 6), 'b': [7, 8]}},
    [(10, {'a': 20, 'b': 30}), [40, 50], {'c': 60, 'd': 70}],
    {'floats': [1.23, 4.56], 'strings': ('abc', 'def'), 'bools': [True, False, True]},
    [complex(1, 2), {'real': 3, 'imag': 4}, (5.0, 6.0)],
]

def test_implementation(name, flatten, unflatten, flatten_structure=None, unique_unflatten=True, iterations=1_000):
    flatten_times = []
    unflatten_times = []
    for data in test_cases:
        flat = flatten(data)
        if flatten_structure is None:
            unflat = unflatten(flat)
        else:
            structure = flatten_structure(data)
            unflat = unflatten(flat, structure)

        compare(data, unflat)
        assert compare(data, unflat), "Unflattened data does not match original"

        fn = lambda: flatten(data)
        flatten_times.append(timeit.timeit(fn, number=iterations))

        if flatten_structure is None:
            fn = lambda: unflatten(flat)
        else:
            fn = lambda: unflatten(flat, structure)
        unflatten_times.append(timeit.timeit(fn, number=iterations))

    print(f'{np.mean(flatten_times):.6f}: {name} flatten time')
    if unique_unflatten:
        print(f'{np.mean(unflatten_times):.6f}: {name} unflatten time')

def test_rust_implementation(iterations=1_000):
    flatten_times = []
    unflatten_times = []
    for data in test_cases:
        flattener = rust_flatten.Flattener()
        flat = flattener.flatten(data)
        unflat = flattener.unflatten(flat)

        compare(data, unflat)
        assert compare(data, unflat), "Unflattened data does not match original"

        flatten_times.append(timeit.timeit(lambda: flattener.flatten(data), number=iterations))
        unflatten_times.append(timeit.timeit(lambda: flattener.unflatten(flat), number=iterations))

    print(f'{np.mean(flatten_times):.6f}: Rust flatten time')
    print(f'{np.mean(unflatten_times):.6f}: Rust unflatten time')

if __name__ == '__main__':
    iterations = 10_000
    test_implementation(
        'Numba Python',
        python_flatten.numba_flatten,
        python_flatten.unflatten,
        python_flatten.flatten_structure,
        unique_unflatten=False,
        iterations=iterations,
    )
    test_implementation(
        'Recursive Cython',
        cython_flatten.recursive_flatten,
        cython_flatten.unflatten,
        python_flatten.flatten_structure,
        unique_unflatten=True,
        iterations=iterations,
    )
    test_implementation(
        'Iterative Cython',
        cython_flatten.iterative_flatten,
        cython_flatten.unflatten,
        python_flatten.flatten_structure,
        unique_unflatten=False,
        iterations=iterations,
    )
    test_implementation(
        'Iterative Python',
        python_flatten.flatten,
        python_flatten.unflatten,
        python_flatten.flatten_structure,
        iterations=iterations,
    )
    test_implementation(
        'Recursive Python',
        python_flatten.naive_flatten,
        python_flatten.unflatten,
        python_flatten.flatten_structure,
        unique_unflatten=False,
        iterations=iterations,
    )
    test_implementation(
        'C',
        c_flatten.flatten,
        c_flatten.unflatten,
        None,
        unique_unflatten=True,
        iterations=iterations,
    )
    test_rust_implementation(iterations=iterations)