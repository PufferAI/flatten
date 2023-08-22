PufferLib needed an optimized flatten and unflatten. 

Install setuptools and setuptools_rust and then build with python setup.py build_ext --inplace

I have been wanting to try out different Python extension options for a while, so this was the perfect excuse. I tested a few different implementation tricks and:

- Native Python
- Cython
- Numba
- C
- Rust

The clear winner is Cython for speed, stability, and ease of development:

0.115050: Numba Python flatten time
0.002302: Recursive Cython flatten time
0.010454: Recursive Cython unflatten time
0.004905: Iterative Cython flatten time
0.028832: Iterative Python flatten time
0.039415: Iterative Python unflatten time
0.027055: Recursive Python flatten time
0.037220: C flatten time
0.010061: C unflatten time
0.036438: Rust flatten time
0.044783: Rust unflatten time

I am sure you could optimize the C and Rust implementations plenty, but I spent more time on each of those than I did on the Cython version. The main issue isn't even the languages themselves: you have to work with a rather clunky Python object type conversion system. This is painless in Cython. Feel free to PR improvements and new extensions. A couple limitations I am aware of:

- C implementation is slightly different and has some corner cases
- Numba just doesn't work... this isn't the type of code that the jit is designed for... but Cython works without much more effort anyways and doesn't spam warnings everywhere.
