# rpgPy

RpgPy is a Python / Cython software for reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) Level 1 and Level 2 binary files.

Installation
------------

``` 
$ pip3 install rpgpy
```
NOTE: old `pip` versions will not automatically install Cython which is a build-dependency for rpgPy. 
In this case, first upgrade `pip` with `$ pip3 install --upgrade pip` or install Cython manually with `$ pip3 install cython`. You also need to have a C-compiler installed because the Cython code is compiled locally during the rpgPy installation.

Usage
-----

```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```

