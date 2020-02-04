# rpgPy

RpgPy is a Python / Cython software for reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) Level 0 and Level 1 binary files.

# Installation

## From PyPI
``` 
$ pip3 install rpgpy
```
NOTE: Old `pip` versions do not automatically install Cython which is a build-dependency for rpgPy. 
In this case, first upgrade `pip` with `$ pip3 install --upgrade pip` or install Cython manually with `$ pip3 install cython`.

You also need to have a C-compiler because Cython code is compiled locally during the rpgPy installation. If you get an error about missing `Python.h`, you need to install the missing header files with `$ sudo apt install python3-dev` (or similar).

## From source
``` 
$ git clone  https://github.com/actris-cloudnet/rpgpy/
$ cd rpgpy/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install .
```

# Usage

## Reading RPG binary file
```python
>>> header, data = rpgpy.read_rpg('rpg_file.LV0')
```
By default, the *header* and *data* dictionary key names are taken from the RPG manual. Optionally, 
more explicit key names can be chosen:
```python
>>> header, data = read_rpg('rpg_file.LV0', rpg_names=False)
```
### Converting to NetCDF4
```python
>>> rpgpy.rpg2nc('rpg_file.LV0', 'rpg_file.nc')
```
In addition to the default global attributes, it is possible to provide 
additional ones via a dictionary:
```python
>>> attr = {'attr1': 'foo', 'attr2': 42}
>>> rpgpy.rpg2nc('rpg_file.LV0', 'rpg_file.nc', global_attr=attr)
```

Performance
-----------
For reading RPG binary files, depending on the radar settings, RpgPy is roughly 20-30 times faster than equivalent native Python or Matlab implementations.

