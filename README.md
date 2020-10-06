# rpgPy

![](https://github.com/actris-cloudnet/rpgpy/workflows/RpgPy%20CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/rpgPy.svg)](https://badge.fury.io/py/rpgPy)

RpgPy is a Python / Cython software for reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) Level 0 and Level 1 binary files.

# Installation

## From PyPI
```
$ python3 -m pip install rpgpy
```
NOTE: You need to have a C-compiler because Cython code is compiled locally during the rpgPy installation.
If you get an error about missing `Python.h`, you need to install the missing header files with `$ sudo apt install python3-dev` (or similar).

## From source
``` 
$ git clone  https://github.com/actris-cloudnet/rpgpy/
$ cd rpgpy/
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ python3 -m pip install --upgrade pip
(venv) $ python3 -m pip install .
(venv) $ python3 setup.py build_ext --inplace
```

# Usage

## Reading RPG binary file
```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```
By default, the ```header``` and ```data``` dictionary key names are taken from the RPG manual. Optionally, 
more explicit key names can be chosen:
```python
>>> header, data = read_rpg('rpg_file.LV0', rpg_names=False)
```
### Converting Level 0 to NetCDF4
```python
>>> from rpgpy import rpg2nc
>>> rpg2nc('rpg_file.LV0', 'rpg_file.nc')
```
In addition to the default global attributes, it is possible to provide 
additional ones via a dictionary:
```python
>>> attr = {'attr1': 'foo', 'attr2': 42}
>>> rpg2nc('rpg_file.LV0', 'rpg_file.nc', global_attr=attr)
```
Several RPG files can be concatenated to singe netCDF file using wildcard.
This can lead to very large netCDF file.
```python
>>> rpg2nc('/path/to/files/*.LV0', 'huge_file.nc')
```

## Tests
Run unit tests:
```
(venv) $ pytest
```

Run end-to-end tests:
```
(venv) $ for f in tests/e2e/*/main.py; do $f; done
```


## Performance
For reading RPG binary files, depending on the radar settings, RpgPy is roughly 20-30 times faster than equivalent native Python or Matlab implementations.

