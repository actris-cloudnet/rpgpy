# Changelog

## 0.10.2

- Fix bug causing crash with version 2 data

## 0.10.1

Bug fixes

## 0.10.0

- `output_directory` and `recursive` keyword arguments, and return value to `rpg2nc_multi`
- Minor optimization of `spectra2moments`
- `spectra2nc` function for creating custom Level 1 file
- API documentation
- Change `ldr`to `zdr` with STSR radar-mode measurements
- Small bug fixes


## 0.9.0

- `rpg2nc_multi` function to convert several rpg files to corresponding netCDF files

## 0.8.0

This release adds function to calculate radar moments from Level 0 data.

## 0.7.2

Adds vertical / horizontal sensitivity limit variables.

## 0.7.1

Fixes serious bug that caused L0 spectral blocks to be read in wrong order in case of several blocks per spectrum

## 0.7.0

Mask zero-values from multidimensional arrays in the created netcdf files

## 0.6.1

Fixes Level 1 reading with dual polarization STSR-mode files

## 0.6.0

- Level 1 data support to `rpg2nc`
- Bug fixes

## 0.5.0

This release:

- Fixes bug in datestamp to date conversion
- Adds support for Level 1 V4 data
- Adds support for Python 3.8
- Adds first unit and end-to-end tests and Github Actions CI
- Fixes installation instructions


## 0.4.0

This version fixes spectral matrices so that the difference chirps correspond to each other.

## 0.3.1

Version `0.3.1.` adds bug fixes.

## 0.3.0
