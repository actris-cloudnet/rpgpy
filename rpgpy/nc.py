"""Module for writing netCDF file."""
import glob
import uuid
from typing import Tuple, Optional
import numpy.ma as ma
from numpy.testing import assert_array_equal
import netCDF4
from tqdm import tqdm
from rpgpy import read_rpg, utils
import rpgpy.metadata
import os
import logging

CWD = os.getcwd()

# Not yet sure how to choose the variables to be written
SKIP_ME = ('ProgName', 'CustName', 'HAlts', 'TAlts', 'StartTime', 'StopTime')


def rpg2nc(path_to_files: str, output_file: str, global_attr: Optional[dict] = None) -> None:
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
    metadata = rpgpy.metadata.METADATA
    metadata = _fix_metadata(metadata, header)
    logging.info('Writing compressed netCDF4 file...')
    _create_dimensions(f, header, level)
    _write_initial_data(f, header, metadata)
    _write_initial_data(f, data, metadata)
    if len(files) > 1:
        for file in tqdm(files[1:]):
            header, data = read_rpg(file)
            _check_header_consistency(f, header)
            _append_data(f, data, metadata)

    _create_global_attributes(f, global_attr, level)
    f.close()
    logging.info('..done.')


def rpg2nc_multi(file_directory: Optional[str] = CWD,
                 base_name: Optional[str] = None,
                 include_lv0: Optional[bool] = True,
                 global_attr: Optional[dict] = None) -> None:
    """Converts all files with extension ['.LV0', '.LV1', '.lv0', 'lv1']
    if include_lv0 is set to True (default); otherwise, it does it just for
    ['.LV1','.lv1'] contained in all the subdirectories of the specified folder.
    By default, it will write the new files with the same name of the original ones,
    just adding the extension 'nc' within directory where the program is executed.

    Args:
        file_directory (str, default: current directory): Root directory from which the function
            will start looking for files to convert.
        include_lv0 (bool, default: True): option to include Level 0 files or not.
        global_attr (dict, optional): Additional global attributes.
        base_name (str, optional): Base name for new filenames.
    """
    for filepath in _generator_files(file_directory, include_lv0):
        logging.info(f'Converting file: {filepath}')
        try:
            prefix = f'{base_name}_' if base_name is not None else ''
            new_filename = f'{prefix}{_new_filename(filepath)}'
            rpg2nc(filepath, new_filename, global_attr)
        except IndexError as err:
            logging.warning(f'############### File {filepath} has not been converted: {err}')
        logging.info("Success!")
    logging.info('-----> Files should be finished!')


def _check_header_consistency(f: netCDF4.Dataset, header: dict) -> None:
    """Checks if header data is identical in all converted files."""
    for key, array in header.items():
        if key in f.variables:
            try:
                assert_array_equal(array, f.variables[key])
            except AssertionError:
                print('Warning: inconsistent header data in ' + key, array, f.variables[key][:])


def _create_dimensions(f: netCDF4.Dataset, header: dict, level: int) -> None:
    f.createDimension('time', None)
    f.createDimension('range', header['RAltN'])
    if level == 0:
        f.createDimension('spectrum', max(header['SpecN']))
        f.createDimension('chirp', header['SequN'])


def _write_initial_data(f: netCDF4.Dataset, data: dict, metadata: dict) -> None:
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        fill_value = 0 if array.ndim > 1 and not ma.isMaskedArray(array) else None
        var = f.createVariable(metadata[key].name, _get_dtype(array),
                               _get_dim(f, array), zlib=True, complevel=3,
                               shuffle=False, fill_value=fill_value)
        var[:] = array
        _set_attributes(var, key, metadata)


def _set_attributes(obj, key: str, metadata: dict) -> None:
    for attr_name in ('long_name', 'units', 'comment'):
        value = getattr(metadata[key], attr_name)
        if value:
            setattr(obj, attr_name, value)
    obj.rpg_manual_name = key


def _append_data(f: netCDF4.Dataset, data: dict, metadata: dict) -> None:
    ind0 = len(f.variables['time'])
    ind1 = ind0 + data['Time'].shape[0]
    for key, array in data.items():
        if key in SKIP_ME:
            continue
        key = metadata[key].name
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


def _generator_files(dir_name: str, include_lv0: bool):
    """"Internal function that creates a generator with file paths
    of level0 (if 'include_lv0' switch is True) and level1 files.
    """
    includes = ('.lv1',) if include_lv0 is False else ('.lv0', 'lv1')
    for subdir, dirs, files in sorted(os.walk(dir_name)):
        for file in files:
            if file.lower().endswith(includes):
                yield os.path.join(subdir, file)


def _new_filename(filepath):
    return f'{os.path.split(filepath)[-1]}.nc'


def _fix_metadata(metadata: dict, header: dict) -> dict:
    fixed_metadata = metadata.copy()
    if header['DualPol'] == 2:
        fixed_metadata['RefRat'] = rpgpy.metadata.Meta(
            name='zdr',
            long_name='Differential Reflectivity Ratio'
        )
    return fixed_metadata
