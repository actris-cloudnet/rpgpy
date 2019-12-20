# rpgPy

RpgPy is a Python / Cython software for reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) binary files.

Installation
------------

``` 
$ pip3 install cython && pip3 install rpgpy
```

Usage
-----

```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```

