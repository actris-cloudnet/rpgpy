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
### Converting a single file to NetCDF4
```python
>>> from rpgpy import rpg2nc
>>> rpg2nc('rpg_file.LV0', 'rpg_file.nc')
```
This works for both Level 0 and Level 1 files.

In addition to the default global attributes, it is possible to provide 
additional ones via a dictionary:
```python
>>> attr = {'attr1': 'foo', 'attr2': 42}
>>> rpg2nc('rpg_file.LV0', 'rpg_file.nc', global_attr=attr)
```
Several RPG files can be concatenated to singe netCDF file using wildcard.
With Level 0 data, this can lead to a very large netCDF file.
```python
>>> rpg2nc('/path/to/files/*.LV0', 'huge_file.nc')
```

### Converting multiple files to NetCDF4
It is possible to convert multiple lv0 or lv1 files with the following function.
Every file with extension .LV0, .lv0, .LV1 or .lv1 in every subdirectory of the specified path will be included in the convertion.  
Optionally, the user can exclude level 0 files by switching to `False` the argument `include_lv0`; by default it will include them.
```python
>>> from rpgpy import rpg2nc_multi
>>> rpg2nc_multi('/path/to/myfiles', include_lv0=True, base_name"foo")
```
If no path is made explicit, the function will by default take as argument the current directory
and write the converted file in it.  
If the parameter `base_name` is specified, the function will rename the new files as `basename_oldname`.

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

## License
MIT
