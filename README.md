# rpgPy

![](https://github.com/actris-cloudnet/rpgpy/workflows/RpgPy%20CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/rpgPy.svg)](https://badge.fury.io/py/rpgPy)

RpgPy is a Python / Cython software for
* Reading [RPG cloud radar](https://www.radiometer-physics.de/products/microwave-remote-sensing-instruments/94-ghz-fmcw-doppler-cloud-radar/) Level 0 and Level 1 binary files
* Calculating spectral moments from RPG Level 0 data
* Converting RPG binary data to [netCDF4](https://www.unidata.ucar.edu/software/netcdf/) format


# Installation

## From PyPI

    python3 -m pip install rpgpy

NOTE: A C-compiler is required because the Cython code is compiled locally during installation.
If you get an error about missing `Python.h`, you need to install the missing header files with `$ apt install python3-dev` (or similar).

## From source

    git clone  https://github.com/actris-cloudnet/rpgpy/
    cd rpgpy/
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install .
    python3 setup.py build_ext --inplace

# Quickstart

### Converting RPG binary files into netCDF4
```python
>>> from rpgpy import rpg2nc
>>> rpg2nc('rpg-data.LV1', 'rpg-file.nc')
```
This writes a compressed netCDF4 file and works with both Level 0 and Level 1 data.

Several RPG files can be concatenated into singe netCDF file using wildcard.
With Level 0 data, this can lead to a very large file.
```python
>>> rpg2nc('/path/to/files/*.LV0', 'huge-file.nc')
```

[API reference of `rpg2nc`](#rpg2nc)

### Converting multiple files individually
Multiple RPG files can be converted into corresponding individual netCDF4 files using `rpg2nc_multi`.
```python
>>> from rpgpy import rpg2nc_multi
>>> filenames = rpg2nc_multi(file_directory='/path/to/files')
```
Default functionality is that every file with an extension `.LV0`, `.lv0`, `.LV1` or `.lv1`
in every subdirectory of the specified path will be converted.

[API reference of `rpg2nc_multi`](#rpg2nc_multi)

### Creating custom Level 1 netCDF4 file
`rpgpy` can estimate spectral moments from Level 0 data. The estimation is based on the most
prominent peak of each time / range point.
```python
>>> from rpgpy import spectra2nc
>>> spectra2nc('rpg-data.LV0', 'level1.nc')
```
This calculates spectral moments from Level 0 data and writes the results in a netCDF4 file.

[API reference of `spectra2nc`](#spectra2nc)

### Reading RPG binary file
If you don't need the netCDF4 file:
```python
>>> from rpgpy import read_rpg
>>> header, data = read_rpg('rpg-data.LV1')
```

[API reference of `read_rpg`](#read_rpg)

### Calculating spectral moments
```python
>>> from rpgpy import read_rpg, spectra2moments
>>> header, data = read_rpg('rpg-data.LV0')
>>> moments = spectra2moments(data, header)
```
This works only with Level 0 data.

[API reference of `spectra2moments`](#spectra2moments)

## API reference

### Index
* [rpg2nc](#rpg2nc)
* [rpg2nc_multi](#rpg2nc_multi)
* [spectra2nc](#spectra2nc)
* [read_rpg](#read_rpg)
* [spectra2moments](#spectra2moments)

##
### `rpg2nc`

Convert RPG cloud radar file(s) into single netCDF file.

```python
rpg2nc(path_to_files, output_file, **kwargs)
```

Positional arguments:

| Name            | Type                        | Description                                                                                     |
|:----------------|:----------------------------|:------------------------------------------------------------------------------------------------|
| `path_to_files` | `str` &#124; `pathlib.Path` | Filename of single file, or multiple files identified using a wildcard, e.g., `/foo/bar/*.LV0`. |
| `output_file`   | `str` &#124; `pathlib.Path` | Output file name.                                                                               |


Keyword arguments:

| Name          | Type   | Default value | Description                   |
|:--------------|:-------|:--------------|:------------------------------|
| `global_attr` | `dict` | `None`        | Additional global attributes. |


##
### `rpg2nc_multi`
Convert RPG cloud radar files into several corresponding netCDF files.
```python
filenames = rpg2nc_multi(**kwargs)
```
Default functionality:
* Input files are searched recursively starting from the current working directory
* Files with the suffix `.LV0`, `.lv0`, `.LV1` or `.lv1` suffix are converted
* netCDF4 files are written to the current working directory

Keyword arguments:

| Name               | Type                        | Default value             | Description                                          |
|:-------------------|:----------------------------|:--------------------------|:-----------------------------------------------------|
| `file_directory`   | `str` &#124; `pathlib.Path` | current working directory | Root path of the search.                             |
| `output_directory` | `str` &#124; `pathlib.Path` | current working directory | Path name where the netCDF4 files are written.       |
| `include_lv0`      | `bool`                      | `True`                    | If `False`, excludes Level 0 files.                  |
| `recursive`        | `bool`                      | `True`                    | If `False`, does not search input files recursively. |
| `base_name`        | `str`                       | `None`                    | Optional filename prefix for the converted files.    |
| `global_attr`      | `dict`                      | `None`                    | Additional global attributes.                        |

Returns:

| Type   | Description                                                 |
|:-------|:------------------------------------------------------------|
| `list` | Full paths of the successfully created netCDF files.        |

##
### spectra2nc
Calculate moments from RPG Level 0 spectra and write a netCDF4 file.
```python
spectra2nc(input_file, output_file, **kwargs)
```

Positional arguments:

| Name          | Type                        | Description                   |
|:--------------|:----------------------------|:------------------------------|
| `input_file`  | `str` &#124; `pathlib.Path` | Filename of RGP Level 0 file. |
| `output_file` | `str` &#124; `pathlib.Path` | Output file name.             |


Keyword arguments:

| Name           | Type   | Default value | Description                                         |
|:---------------|:-------|:--------------|:----------------------------------------------------|
| `global_attr`  | `dict` | `None`        | Additional global attributes.                       |
| `n_points_min` | `int`  | 4             | Minimum number of points in a proper spectral line. |


##
### `read_rpg`

Read RPG cloud radar binary file.

```python
header, data = read_rpg(filename, **kwargs)
```

Positional arguments:

| Name       | Type                        | Description                                                 |
|:-----------|:----------------------------|:------------------------------------------------------------|
| `filename` | `str` &#124; `pathlib.Path` | Filename of RPG cloud radar Level 1 or Level 0 binary file. |

Keyword arguments:

| Name        | Type     | Default value | Description                                                                                       |
|:------------| :------  | :---          |:--------------------------------------------------------------------------------------------------|
| `rpg_names` | `bool`   | `True`        | If `True`, uses RPG manual names in the returned dictionary, else uses more human-readable names. |

Returns:

| Type    | Description                                                 |
|:--------|:------------------------------------------------------------|
| `tuple` | 2-element tuple containing `header` and `data` dictionary.  |


##
### `spectra2moments`

Calculate spectral moments from Level 0 spectral data. A call to [`read_rpg`](#read_rpg)
is required before using this function.

```python
moments = spectra2moments(data, header, **kwargs)
```

Positional arguments:

| Name     | Type   | Description                                             |
|:---------|:-------|:--------------------------------------------------------|
| `data`   | `dict` | Level 0 data dictionary from [`read_rpg`](#read_rpg).   |
| `header` | `dict` | Level 0 header dictionary from [`read_rpg`](#read_rpg). |

Keyword arguments:

| Name           | Type    | Default value | Description                                                 |
|:---------------|:--------|:--------------|:------------------------------------------------------------|
| `spec_var`     | `str`   | `"TotSpec"`   | Spectral variable to be analyzed: `"TotSpec"` or `"HSpec"`. |
| `fill_value`   | `float` | -999.0        | Value for the clear sky data points.                        |
| `n_points_min` | `int`   | 4             | Minimum number of points in a proper spectral line.         |


Returns:

| Type       | Description                                                                                                                                                                             |
|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `dict`     | Dictionary containing `Ze` (reflectivity), `MeanVel` (mean velocity), `SpecWidth` (spectral width), `Skewn` (skewness) and `Kurt` (kurtosis), which are 2D numpy arrays (time x range). |


## Development

Install test-dependencies and [pre-commit](https://pre-commit.com/) hooks:

    python3 -m pip install -e .[test,dev]
    pre-commit install

Compile Cython (repeat if you change `.pyx` files):

    python3 setup.py build_ext --inplace

### Tests

Run unit tests:

    pytest

Run end-to-end tests:

    for f in tests/e2e/*/*runner.py; do $f; done

Force `pre-commit` checks of all files:

    pre-commit run --all


## Performance
For reading RPG binary files, depending on the radar settings, RpgPy is roughly 20-30 times faster
than equivalent native Python or Matlab implementations.

## License
MIT
