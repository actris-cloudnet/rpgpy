# Changelog

## 0.15.6 – 2024-05-10

- Fix overflow in n_blocks

## 0.15.5 – 2024-04-23

- Adjust GitHub Actions workflows

## 0.15.4 – 2024-04-23

- Fix publish GitHub Actions workflow

## 0.15.3 – 2024-04-23

- Update workflow

## 0.15.2 – 2024-04-23

- Raise RPGFileError if corrupted file code

## 0.15.1 – 2023-11-30

- Build and upload binary wheels to PyPI

## 0.15.0 – 2023-11-22

- Revise time conversion functions

## 0.14.6 – 2023-10-03

- Skip StartTime and StopTime check (with older file versions)

## 0.14.5 – 2023-09-25

- Distribute package only as source distribution

## 0.14.4 – 2023-09-25

- Remove DEF that will be deprecated
- Unlock numba version

## 0.14.3 – 2023-09-25

- Raise RPGFileError if file reading fails

## 0.14.2 – 2023-05-04

- Support Python 3.11

## 0.14.1 – 2023-05-04

- Fix numpy warnings
- Change velocity vectors to ordinary numpy array

## 0.14.0 – 2023-04-13

- Add support for RPG version 1 files
- Change RPG file version 3 to 3.5
- Write `rpg_file_version` attribute to netCDF output
- Add py.typed to enable type checking

## 0.13.1 – 2022-11-28

- Fix mask in `decode_rpg_status_flags`

## 0.13.0 – 2022-11-18

- Add `decode_rpg_status_flags` function
- Add `rpg_seconds2datetime64` to quickly convert array of timestamps

## 0.12.1 – 2022-10-10

- Add Windows and Mac to CI tests
- Add Python 3.10
- Update numpy version requirement

## 0.12.0 – 2022-05-11

- Accept Path object as filename
- Add release dates to CHANGELOG.md
- Run pytest-flakefinder on CI
- Separate test and dev dependencies

## 0.11.0 – 2022-03-31

- Use default `zlib` compression settings
- Lock maximum `numpy` version required by `numba`
- Add CHANGELOG.md
- Add `pre-commit` for checking the code
- Reformat the code with `black`

## 0.10.2 – 2021-11-09

- Fix bug causing crash with version 2 data

## 0.10.1 – 2021-10-13

Bug fixes

## 0.10.0 – 2021-10-04

- `output_directory` and `recursive` keyword arguments, and return value to `rpg2nc_multi`
- Minor optimization of `spectra2moments`
- `spectra2nc` function for creating custom Level 1 file
- API documentation
- Change `ldr`to `zdr` with STSR radar-mode measurements
- Small bug fixes

## 0.9.0 – 2021-09-03

- `rpg2nc_multi` function to convert several rpg files to corresponding netCDF files

## 0.8.0 – 2021-02-24

This release adds function to calculate radar moments from Level 0 data.

## 0.7.2 – 2021-02-16

Adds vertical / horizontal sensitivity limit variables.

## 0.7.1 – 2021-02-12

Fixes serious bug that caused L0 spectral blocks to be read in wrong order in case of several blocks per spectrum

## 0.7.0 – 2021-01-05

Mask zero-values from multidimensional arrays in the created netcdf files

## 0.6.1 – 2021-01-04

Fixes Level 1 reading with dual polarization STSR-mode files

## 0.6.0 – 2020-12-08

- Level 1 data support to `rpg2nc`
- Bug fixes

## 0.5.0 – 2020-10-05

This release:

- Fixes bug in datestamp to date conversion
- Adds support for Level 1 V4 data
- Adds support for Python 3.8
- Adds first unit and end-to-end tests and Github Actions CI
- Fixes installation instructions

## 0.4.0 – 2020-07-01

This version fixes spectral matrices so that the difference chirps correspond to each other.

## 0.3.1 – 2020-05-11

Version `0.3.1.` adds bug fixes.

## 0.3.0 – 2020-05-11

First stable release.
