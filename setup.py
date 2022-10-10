from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup

extensions = [
    Extension(
        name="rpgpy.data",
        sources=["rpgpy/data.pyx"],
    ),
]

version: dict = {}
with open("rpgpy/version.py", encoding="utf-8") as f:
    exec(f.read(), version)  # pylint: disable=W0122

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="rpgPy",
    description="Cython code for reading binary files from RPG cloud radar.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simo Tukiainen",
    author_email="simo.tukiainen@fmi.fi",
    version=version["__version__"],
    url="https://github.com/actris-cloudnet/rpgpy",
    license="MIT License",
    install_requires=["numpy", "cython", "netCDF4", "tqdm", "pytz", "numba"],
    extras_require={
        "test": [
            "pytest-flakefinder",
            "pylint",
            "mypy",
            "types-pytz",
        ],
        "dev": ["pre-commit"],
    },
    include_package_data=True,
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    ext_modules=cythonize(extensions, language_level=3),
)
