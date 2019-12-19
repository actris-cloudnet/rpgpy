# rpgPy

RpgPy is a Python / Cython implementation for reading RPG cloud radar binary files.

Installation
------------

```
$ pip3 install cython 
$ pip3 install rpgpy
```

Usage
-----

```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```

