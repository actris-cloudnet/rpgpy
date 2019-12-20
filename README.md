# rpgPy

RpgPy is a Python / Cython software for reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) binary files.

Installation
------------

``` 
$ pip3 install rpgpy
```
If you have an old pip version, the command above fails to install Cython which is a build-dependency for rpgPy. 
In this case, first install Cython with `$ pip3 install cython`. You also need to have a C-compiler installed because the Cython code is compiled locally during the installation.

Usage
-----

```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```

