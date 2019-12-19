from distutils.core import setup
from Cython.Build import cythonize

setup(name='RPG Reader testing',
      ext_modules=cythonize("rpg_cython.pyx",
                            annotate=True,
                            language_level=3),
      )
