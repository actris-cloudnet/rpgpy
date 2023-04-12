from Cython.Build import cythonize
from setuptools import Extension, setup

extensions = [
    Extension(
        name="rpgpy.data",
        sources=["rpgpy/data.pyx"],
    ),
]

setup(ext_modules=cythonize(extensions, language_level=3))
