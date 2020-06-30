"""Module for reading RPG 94 GHz radar header."""
import numpy as np
from rpgpy import utils


def read_rpg_header(file_name):
    """Reads header from RPG binary file.

    Supports Level 0/1 and version 2/3.

    Args:
        file_name (str): name of the file.

    Returns:
        tuple: 2-element tuple containing the header (as dict) and file position.

    """
    def read(*fields):
        block = np.fromfile(file, np.dtype(list(fields)), 1)
        for name in block.dtype.names:
            array = block[name][0]
            if utils.isscalar(array):
                header[name] = array
            else:
                header[name] = np.array(array, dtype=_get_dtype(array))

    header = {}
    file = open(file_name, 'rb')

    read(('FileCode', 'i4'),
         ('HeaderLen', 'i4'))

    level, version = utils.get_rpg_file_type(header)

    if version > 2:
        read(('StartTime', 'uint32'),
             ('StopTime', 'uint32'))

    read(('CGProg', 'i4'),
         ('ModelNo', 'i4'))

    header['ProgName'] = _read_string(file)
    header['CustName'] = _read_string(file)

    read(('Freq', 'f'),
         ('AntSep', 'f'),
         ('AntDia', 'f'),
         ('AntG', 'f'),
         ('HPBW', 'f'))

    if level == 0:
        read(('Cr', 'f'))

    read(('DualPol', 'i1'))

    if level == 0:
        read(('CompEna', 'i1'),
             ('AntiAlias', 'i1'))

    read(('SampDur', 'f'),
         ('GPSLat', 'f'),
         ('GPSLong', 'f'),
         ('CalInt', 'i4'),
         ('RAltN', 'i4'),
         ('TAltN', 'i4'),
         ('HAltN', 'i4'),
         ('SequN', 'i4'))

    n_levels, n_temp, n_humidity, n_chirp = _get_number_of_levels(header)

    read(('RAlts', _dim(n_levels)),
         ('TAlts', _dim(n_temp)),
         ('HAlts', _dim(n_humidity)))

    if level == 0:
        read(('Fr', _dim(n_levels)))

    read(('SpecN', _dim(n_chirp, 'i4')),
         ('RngOffs', _dim(n_chirp, 'i4')),
         ('ChirpReps', _dim(n_chirp, 'i4')),
         ('SeqIntTime', _dim(n_chirp)),
         ('dR', _dim(n_chirp)),
         ('MaxVel', _dim(n_chirp)))

    if version > 2:
        if level == 0:
            read(('ChanBW', _dim(n_chirp)),
                 ('ChirpLowIF', _dim(n_chirp, 'i4')),
                 ('ChirpHighIF', _dim(n_chirp, 'i4')),
                 ('RangeMin', _dim(n_chirp, 'i4')),
                 ('RangeMax', _dim(n_chirp, 'i4')),
                 ('ChirpFFTSize', _dim(n_chirp, 'i4')),
                 ('ChirpInvSamples', _dim(n_chirp, 'i4')),
                 ('ChirpCenterFr', _dim(n_chirp)),
                 ('ChirpBWFr', _dim(n_chirp)),
                 ('FFTStartInd', _dim(n_chirp, 'i4')),
                 ('FFTStopInd', _dim(n_chirp, 'i4')),
                 ('ChirpFFTNo', _dim(n_chirp, 'i4')),
                 ('SampRate', 'i4'),
                 ('MaxRange', 'i4'))

        read(('SupPowLev', 'i1'),
             ('SpkFilEna', 'i1'),
             ('PhaseCorr', 'i1'),
             ('RelPowCorr', 'i1'),
             ('FFTWindow', 'i1'),
             ('FFTInputRng', 'i4'),
             ('NoiseFilt', 'f4'))

        if level == 0:
            _ = np.fromfile(file, 'i4', 25)
            _ = np.fromfile(file, 'uint32', 10000)

            # adding velocity vectors for each chirp
            for c in range(n_chirp):
                dopp_res = np.divide(2.0 * header['MaxVel'][c], header['SpecN'][c])
                header[f'C{c+1}vel'] = np.linspace(-header['MaxVel'][c] + (0.5 * dopp_res),
                                                   +header['MaxVel'][c] - (0.5 * dopp_res),
                                                   np.max(header['SpecN']))

    file_position = file.tell()
    file.close()

    return header, file_position


def _read_string(file_id):
    """Read characters from binary data until whitespace."""
    str_out = ''
    while True:
        value = np.fromfile(file_id, np.int8, 1)
        if value:
            if value < 0:
                value = 0
            str_out += chr(value)
        else:
            break
    return str_out


def _get_number_of_levels(header):
    for name in ('RAltN', 'TAltN', 'HAltN', 'SequN'):
        yield int(header[name])


def _dim(length, dtype='f'):
    return f"({length},){dtype}"


def _get_dtype(array):
    if array.dtype in (np.int8, np.int32, np.uint32):
        return int
    return float
