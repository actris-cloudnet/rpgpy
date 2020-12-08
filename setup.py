from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

extensions = [Extension(
    name="rpgpy.data",
    sources=["rpgpy/data.pyx"],
    ),
]

version = {}
with open("rpgpy/version.py") as f:
    exec(f.read(), version)


setup(name='rpgPy',
      description='Cython code for reading binary files from RPG cloud radar.',
      author='Simo Tukiainen',
      author_email='simo.tukiainen@fmi.fi',
      version=version['__version__'],
      url='https://github.com/actris-cloudnet/rpgpy',
      license='MIT License',
      install_requires=['numpy', 'cython', 'netCDF4', 'tqdm', 'pytest', 'pytz'],
      include_package_data=True,
      packages=find_packages(),
      python_requires='>=3.6',
      classifiers=[
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 3.6",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering",
      ],
      ext_modules=cythonize(extensions, language_level=3),
      )
