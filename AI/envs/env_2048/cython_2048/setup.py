from setuptools import setup
from Cython.Build import cythonize

setup(
    name='2048 cython implements',
    ext_modules=cythonize(
        "main.pyx",
        annotate=True,
    ),
)
