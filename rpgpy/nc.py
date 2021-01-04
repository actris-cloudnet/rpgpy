"""Module for writing netCDF file."""
import glob
import uuid
from typing import Tuple
import numpy.ma as ma
from numpy.testing import assert_array_equal
import netCDF4
from tqdm import tqdm
from rpgpy import read_rpg, utils
from rpgpy.metadata import METADATA


# Not yet sure how to choose the variables to be written
SKIP_ME = ('ProgName', 'CustName', 'HAlts', 'TAlts',
           'StartTime', 'StopTime')


def rpg2nc(path_to_files: str, output_file: str, global_attr: dict = None) -> None:
    """Converts RPG binary files into a netCDF4 file.

    Args:
        path_to_files (str): Directory containing RPG binary file(s) and optionally
            a wildcard to distinguish between different types of files.
            E.g. '/path/to/data/*.LV0'
        output_file (str): Name of the output file.
        global_attr (dict, optional): Additional global attributes.

    """
    files, level = _get_rpg_files(path_to_files)
    f = netCDF4.Dataset(output_file, 'w', format='NETCDF4_CLASSIC')
    header, data = read_rpg(files[0])
    print('Writing compressed netCDF4 file...')
    _create_dimensions(f, header, level)
    _write_initial_data(f, header)
    _write_initial_data(f, data)
    if len(files) > 1:
        for file in tqdm(files[1:]):
            header, data = read_rpg(file)
            _check_header_consistency(f, header)
            _append_data(f, data)

    _create_global_attributes(f, global_attr, level)
    f.close()
    print('..done.')


def _check_header_consistency(f: netCDF4.Dataset, header: dict) -> None:
    """Checks if header data is identical in all converted files."""
    for key, array in header.items():
        if key in f.variables:
            try:
                assert_array_equal(array, f.variables[key])
            except AssertionError:
                print('Warning: inconsistent header data in ' + key, array,
                      f.variables[key][:])


def _create_dimensions(f: netCDF4.Dataset, header: dict, level: int) -> None:
    f.createDimension('time', None)
    f.createDimension('range', header['RAltN'])
    if level == 0:
        f.createDimension('spectrum', max(header['SpecN']))
        f.createDimension('chirp', header['SequN'])


def _write_initial_data(f: netCDF4.Dataset, data: dict) -> None:
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        var = f.createVariable(METADATA[key].name, _get_dtype(array),
                               _get_dim(f, array), zlib=True, complevel=3,
                               shuffle=False)
        var[:] = array
        _set_attributes(var, key)


def _set_attributes(obj, key: str) -> None:
    for attr_name in ('long_name', 'units', 'comment'):
        value = getattr(METADATA[key], attr_name)
        if value:
            setattr(obj, attr_name, value)
    obj.rpg_manual_name = key


def _append_data(f: netCDF4.Dataset, data: dict) -> None:
    ind0 = len(f.variables['time'])
    ind1 = ind0 + data['Time'].shape[0]
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        key = METADATA[key].name
        if array.ndim == 1:
            f.variables[key][ind0:ind1] = array
        elif array.ndim == 2:
            f.variables[key][ind0:ind1, :] = array
        else:
            f.variables[key][ind0:ind1, :, :] = array


def _get_dtype(array) -> str:
    if 'int' in str(array.dtype):
        return 'i4'
    return 'f4'


def _get_rpg_files(path_to_files: str) -> Tuple[list, int]:
    """Returns list of RPG files for one day sorted by filename and level (0 or 1)."""
    files = glob.glob(path_to_files)
    files.sort()
    if not files:
        raise RuntimeError('No proper RPG binary files found')
    extension = [file[-4:] for file in files]
    if all(ext.lower() == '.lv1' for ext in extension):
        level = 1
    elif all(ext.lower() == '.lv0' for ext in extension):
        level = 0
    else:
        raise RuntimeError('No consistent RPG level (0 or 1) files found.')
    return files, level


def _get_dim(f: netCDF4.Dataset, array) -> tuple:
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


def _create_global_attributes(f: netCDF4.Dataset, global_attr: dict, level: int):
    f.Conventions = 'CF-1.7'
    f.year, f.month, f.day = _get_measurement_date(f)
    f.uuid = uuid.uuid4().hex
    f.history = f"Radar file created: {utils.get_current_time()}"
    f.level = level
    if global_attr and isinstance(global_attr, dict):
        for key, value in global_attr.items():
            setattr(f, key, value)


def _get_measurement_date(file: netCDF4.Dataset) -> list:
    time = file.variables['time'][:]
    date = utils.rpg_seconds2date(ma.min(time), date_only=True)
    assert_array_equal(date, utils.rpg_seconds2date(ma.max(time), date_only=True))
    return date
