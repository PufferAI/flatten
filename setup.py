from pdb import set_trace as T

from setuptools import find_packages, setup, Extension
from setuptools_rust import Binding, RustExtension
from Cython.Build import cythonize

setup(
    name="flatten",
    description="Flatten and unflatten nested data structures",
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy==1.23.3',
    ],
    zip_safe=False,
    rust_extensions=[RustExtension("rust_flatten", binding=Binding.PyO3, path="rust/Cargo.toml")],
    ext_modules = [
        *cythonize("cython_flatten.pyx"),
        Extension(
            'c_flatten',
            ['c_flatten.c'],
            extra_compile_args=[
                '-fPIC',         # Position-independent code (needed for shared libraries)
                '-O3',           # Highest level of optimization
                '-march=native', # Tune for the host CPU
                '-funroll-loops' # Unroll loops for additional performance
            ],
            define_macros=[],
        ),
    ],
    python_requires=">=3.8",
    license="MIT",
    author="Joseph Suarez",
    author_email="jsuarez@mit.edu",
    url="https://github.com/PufferAI/PufferLib",
    keywords=["Puffer", "AI", "RL"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)