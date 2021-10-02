# rpgPy

![](https://github.com/actris-cloudnet/rpgpy/workflows/RpgPy%20CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/rpgPy.svg)](https://badge.fury.io/py/rpgPy)

RpgPy is a Python / Cython software for 
* Reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) Level 0 and Level 1 binary files
* Converting RPG binary data to [netCDF4](https://www.unidata.ucar.edu/software/netcdf/) format
* Calculating spectral moments from RPG Level 0 data

# Installation

## From PyPI
```
$ python3 -m pip install rpgpy
```
NOTE: A C-compiler is required because the Cython code is compiled locally during installation.
If you get an error about missing `Python.h`, you need to install the missing header files with `$ apt install python3-dev` (or similar).

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

# Quickstart

### Reading RPG binary file
```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg_file.LV0')
```
This works for both Level 0 and Level 1 files.

### Converting single file to single netCDF4
```python
>>> from rpgpy import rpg2nc
>>> rpg2nc('rpg_file.LV0', 'rpg_file.nc')
```
This will write a compressed netCDF4 file.

### Converting multiple files to single netCDF4
Several RPG files can be concatenated into singe netCDF file using wildcard.
With Level 0 data, this can lead to a very large netCDF file.
```python
>>> rpg2nc('/path/to/files/*.LV0', 'huge_file.nc')
```

### Converting multiple files to corresponding netCDF4 files
Multiple RPG files can be converted into corresponding individual netCDF4 files using the `rpg2nc_multi` function.
Every file with an extension `.LV0`, `.lv0`, `.LV1` or `.lv1` in every subdirectory of the specified path will be converted.
Optionally, Level 0 files can be excluded by switching `include_lv0` to `False`:
```python
>>> from rpgpy import rpg2nc_multi
>>> rpg2nc_multi('/path/to/files', include_lv0=False)
```
The converted files are written to the current working directory with a `.nc` suffix. 

### Calculating spectral moments
`rpgpy` can estimate spectral moments from Level 0 data. The estimation is based on the most 
prominent peak of each time / range point.
```python
>>> from rpgpy import read_rpg, spectra2moments
>>> header, data = read_rpg('my-file.LV0')
>>> moments = spectra2moments(data, header)
```

## API reference

### `rpg2nc()`

Convert RPG cloud radar file(s) into single netCDF file.

```python
rpg2nc(input: str, output: str, **kwargs)
```

Positional arguments:

|  Name         | Type         | Description                
| :---          | :----------  | :---
| `input`       | `str`        | Filename of single file, or multiple files identified using a wildcard, e.g., `/foo/bar/*.LV0`.   
| `output`      | `str`        | Output file name.


Keyword arguments:

|  Name         | Type         | Default value  | Description
| :---          | :----------  | :---           | :---
| `global_attr` | `dict`       | `{}`           | Additional global attributes. 
| `calc_moments` | `bool`      | `False`        | If `True`, calculates spectral moments from Level 0 data. Has no effect with Level 1 data.
| `n_points_min` | `int`       | 4              | Minimum number of points in a proper spectral line. Has no effect with Level 1 data or if `calc_moments = False`.


##
### `rpg2nc_multi()`

Convert RPG cloud radar files into several corresponding netCDF files. Input files are searched 
recursively and the output files are written in the current working directory.

```python
rpg2nc_multi(**kwargs)
```
In addition to the same keyword arguments than `rpg2nc`, this function also accepts the following keyword arguments:

|  Name              | Type        | Default value              | Description                                    
| :---               | :------     | :---                       | :---                                           
| `file_directory`   | `str`       | current working directory  | Root path to be searched recursively.  
| `include_lv0`      | `bool`      | `True`                     | If `False`, exclude Level 0 files.
| `base_name`        | `str`       | `None`                     | Optional prefix for the converted files.
| `output_directory` | `str`       | current working directory  | Path name where the files are written.

##
### `read_rpg()`

Read RPG cloud radar binary file.

```python
header, data = read_rpg(filename: str, rpg_names: bool = True)
```

Positional arguments:

| Name        | Type     | Description                                | 
| :---        | :------  | :---                                       |
| `filename`  | `str`    | Filename of RPG cloud radar Level 1 or Level 0 binary file. |

Keyword arguments:

|  Name       | Type     | Default value | Description
| :---        | :------  | :---          | :---                                       |
| `rpg_names` | `bool`   | `True`        | If `True`, uses RPG manual names in the returned dictionary, else uses more human-readable names.|

Returns:

| Type        | Description                                                | 
| :---------- | :---                                                       |
| `tuple`     | 2-element tuple containing `header` and `data` dictionary. |


##
### `spectra2moments()`

Calculate spectral moments from Level 0 spectral data. A call to `read_rpg()` is required before using this function.

```python
moments = spectra2moments(data: dict, header: dict, **kwargs)
```

Positional arguments:

|  Name          | Type       | Description                                    
| :---           | :--------  | :---                                           
| `data`         | `dict`     | Level 0 data dictionary from `read_rpg()`.      
| `header`       | `dict`     | Level 0 header dictionary from `read_rpg()`.    

Keyword arguments:

|  Name          | Type       | Default value | Description                                    
| :---           | :--------  | :---          | :---                                           
| `spec_var`     | `str`      | `"TotSpec"`   | Spectral variable to be analyzed: `"TotSpec"` or `"HSpec"`.
| `fill_value`   | `float`    | -999.0        | Value for the clear sky data points.
| `n_points_min` | `int`      | 4             | Minimum number of points in a proper spectral line.


Returns:

| Type      | Description                                                 | 
| :-------  | :---                                                        |
| `dict`    | Dictionary containing `Ze` (reflectivity), `MeanVel` (mean velocity), `SpecWidth` (spectral width), `Skewn` (skewness) and `Kurt` (kurtosis), which are 2D numpy arrays (time x range).|


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
For reading RPG binary files, depending on the radar settings, RpgPy is roughly 20-30 times faster
than equivalent native Python or Matlab implementations.

## License
MIT
