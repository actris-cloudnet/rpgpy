"""Module for writing netCDF file."""
import os
import glob
from numpy.testing import assert_array_equal
import netCDF4
from tqdm import tqdm
from rpgpy import read_rpg, utils
from rpgpy.metadata import METADATA


# Not yet sure how to choose the variables to be written
SKIP_ME = ('ProgName', 'CustName')


def rpg2nc(path_to_files, output_file):
    """Converts RPG binary files into a netCDF4 file.

    Args:
        path_to_files (str): Directory containing RPG binary file(s) and optionally 
            a wildcard to distinguish between different types of files. 
            E.g. '/path/to/data/*.LV0'
        output_file (str): Name of the output file.

    """
    files = _get_rpg_files(path_to_files)
    f = netCDF4.Dataset(output_file, 'w', format='NETCDF4_CLASSIC')
    print('Preparing file writing...')
    header, data = read_rpg(files[0])
    _create_dimensions(f, header)
    _create_global_attributes(f)
    _write_initial_data(f, header)
    _write_initial_data(f, data)
    print('Writing compressed netCDF4 file...')
    if len(files) > 1:
        for file in tqdm(files[1:]):
            header, data = read_rpg(file)
            _check_header_consistency(f, header)
            _append_data(f, data)
    f.close()
    print('..done.')


def _check_header_consistency(f, header):
    """Checks if header data is identical in all converted files."""
    for key, array in header.items():
        if key in f.variables:
            try:
                assert_array_equal(array, f.variables[key])
            except AssertionError:
                print('Warning: inconsistent header data in ' + key, array,
                      f.variables[key][:])


def _create_dimensions(f, header):
    f.createDimension('time', None)
    f.createDimension('range', header['RAltN'])
    f.createDimension('spectrum', max(header['SpecN']))
    f.createDimension('chirp', header['SequN'])


def _write_initial_data(f, data):
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        x = f.createVariable(key, _get_dtype(array), _get_dim(f, array),
                             zlib=True, complevel=3, shuffle=False)
        x[:] = array
        _set_attributes(x, key)


def _set_attributes(obj, key):
    for attr_name in ('long_name', 'units', 'comment'):
        value = getattr(METADATA[key], attr_name)
        if value:
            setattr(obj, attr_name, value)


def _append_data(f, data):
    ind0 = len(f.variables['Time'])
    ind1 = ind0 + data['Time'].shape[0]
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        if array.ndim == 1:
            f.variables[key][ind0:ind1] = array
        elif array.ndim == 2:
            f.variables[key][ind0:ind1, :] = array
        else:
            f.variables[key][ind0:ind1, :, :] = array


def _get_dtype(array):
    if 'int' in str(array.dtype):
        return 'i4'
    return 'f4'


def _create_global_attributes(f):
    f.Conventions = 'CF-1.7'


def _get_rpg_files(path_to_files):
    """Returns list of RPG files for one day sorted by filename."""
    files = glob.glob(path_to_files)
    files.sort()
    if not files:
        raise RuntimeError('No proper RPG binary files found')
    return files


def _get_dim(f, array):
    """Finds correct dimensions for a variable."""
    if utils.isscalar(array):
        return ()
    variable_size = ()
    file_dims = f.dimensions
    for length in array.shape:
        try:
            dim = [key for key in file_dims.keys()
                   if file_dims[key].size == length][0]
        except IndexError:
            dim = 'time'
        variable_size = variable_size + (dim,)
    return variable_size
