"""Module for writing netCDF file."""
import os
import datetime
import numpy as np
import numpy.ma as ma
import netCDF4
from rpgpy import read_rpg
from rpgpy.metadata import METADATA


def rpg2nc(path_to_files, output_file, level):
    files = _get_rpg_files(path_to_files, level)
    header, data = read_rpg(files[0])
    f = netCDF4.Dataset(output_file, 'w', format='NETCDF4_CLASSIC')
    _create_dimensions(f, header)
    _create_global_attributes(f, header)
    _write_initial_data(f, data)
    f.close()


def _write_initial_data(f, data):
    for key, array in data.items():
        x = f.createVariable(key, _get_dtype(array), _get_dim(array), zlib=True)
        x[:] = array
        for name in ('long_name', 'units', 'comment'):
            value = getattr(METADATA[key], name)
            if value:
                setattr(x, name, value) 


def _get_dtype(array):
    if 'int' in str(array.dtype):
        return 'i4'
    return 'f4'


def _get_dim(array):
    if array.ndim == 1:
        return ('time')
    elif array.ndim == 2:
        return ('time', 'range')
    return ('time', 'range', 'spectrum')


def _create_dimensions(f, header):
    f.createDimension('time', None)
    f.createDimension('range', header['RAltN'])
    f.createDimension('spectrum', max(header['SpecN']))
    f.createDimension('chirp', header['SequN'])


def _create_global_attributes(f, header):
    f.Conventions = 'CF-1.7'
    

def _get_rpg_files(path_to_files, level):
    """Returns list of RPG files for one day sorted by filename."""
    files = os.listdir(path_to_files)
    files = [f"{path_to_files}{file}" for file in files if file.endswith(str(level))]
    files.sort()
    return files
