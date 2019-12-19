from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize

extensions = [Extension(
    name="rpgpy.rpg_cython",
    sources=["rpgpy/rpg_cython.pyx"],
    ),
]

version = {}
with open("rpgpy/version.py") as f:
    exec(f.read(), version)

#with open('README.md') as f:
#    readme = f.read()

setup(name='rpgPy',
      description='Cython code for reading binary files from RPG cloud radar.',
      #long_description=readme,
      #long_description_content_type='text/markdown',
      author='Simo Tukiainen',
      author_email='simo.tukiainen@fmi.fi',
      version=version['__version__'],
      url='https://github.com/tukiains/rpgpy',
      license='MIT License',
      install_requires=['numpy>=1.16', 'cython>=0.29'],
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
      ext_modules = cythonize(extensions),

)
