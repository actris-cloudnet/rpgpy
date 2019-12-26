"""Module for writing netCDF file."""
import os
import datetime
import numpy as np
import numpy.ma as ma
import netCDF4
from rpgpy import read_rpg


def rpg2nc(path_to_files, output_file, level):
    files = _get_rpg_files(path_to_files, level)
    header, data = read_rpg(files[0])

    f = netCDF4.Dataset(output_file, 'w', format='NETCDF4_CLASSIC')

    _create_dimensions(f, header)
    _create_global_attributes(f, header)

    f.close()


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
