"""RPG cloud radar binary reader in Cython."""
from libc.stdio cimport *
from libc.stdlib cimport free, malloc

import logging
import os

import numpy as np

from rpgpy import header as head
from rpgpy import utils
from rpgpy.metadata import METADATA

from rpgpy.utils import RPGFileError


def read_rpg(file_name: os.PathLike | str, rpg_names: bool = True) -> tuple[dict, dict]:
    """ Reads RPG Level 1 / Level 0 binary file.

    Args:
        file_name: File name.
        rpg_names: If True, uses RPG naming scheme for the returned data dict.
            Otherwise, uses custom names. Default is True.

    Returns:
        2-element tuple containing header (dict) and data (dict).

    """
    file_name_bytes = os.fsencode(file_name)
    logging.debug(f'Reading {file_name}')
    header, _ = head.read_rpg_header(file_name)
    level, version = utils.get_rpg_file_type(header)
    if level == 0:
        data = _read_rpg_l0(file_name_bytes, header)
    else:
        data = _read_rpg_l1(file_name_bytes, header, version)
    if not rpg_names:
        data = _change_keys(data)
        header = _change_keys(header)
        if header['Dual Polarisation'] == 2:
            data['Differential Reflectivity Ratio'] = data.pop('Linear Depolarisation Ratio')
    return header, data


def _change_keys(a_dict: dict) -> dict:
    dict_new = {}
    for key in a_dict.keys():
        dict_new[METADATA[key].long_name] = a_dict[key]
    return dict_new


def _read_rpg_l0(file_name: bytes, header: dict) -> dict:
    """Reads RPG LV0 binary file."""

    cdef:
        char* fname = file_name
        FILE *ptr
        int header_length=0, n_samples=0, sample=0, n=0, m=0
        int alt_ind=0, n_points=0, bins_to_shift=0
        unsigned char n_blocks
        int n_spectra = max(header['SpecN'])
        int n_levels = header['RAltN']
        int compression = header['CompEna']
        int polarization = header['DualPol']
        int anti_alias = header['AntiAlias']
        short int[256] min_ind  # n_blocks is 8 bits
        short int[256] max_ind
        short int[256] n_block_points
        short int[256] spec_ind
        char *is_data = <char *> malloc(n_levels * sizeof(char))
        int *n_samples_at_each_height = <int *> malloc(n_levels * sizeof(int))

    ptr = fopen(fname, "rb")
    fseek(ptr, 4, SEEK_CUR)
    fread(&header_length, 4, 1, ptr)
    fseek(ptr, header_length, SEEK_CUR)
    fread(&n_samples, 4, 1, ptr)

    cdef:
        int [:] SampBytes = np.empty(n_samples, np.int32)
        unsigned int [:] Time = np.empty(n_samples, np.uint32)
        int [:] MSec = np.empty(n_samples, np.int32)
        char [:] QF = np.empty(n_samples, np.int8)
        float [:] RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF,
        float [:] Elev, Azi, Status, TransPow, TransT, RecT, PCT
        float [:, :, :] TotSpec = np.zeros((n_samples, n_levels, n_spectra), np.float32)
        float [:, :, :] HSpec, ReVHSpec, ImVHSpec, RefRat, CorrCoeff, DiffPh, SLDR, SCorrCoeff
        float [:, :] KDP, DiffAtt, TotNoisePow, HNoisePow, MinVel, SLh, SLv
        char [:, :] AliasMsk
        int n_dummy = 3 + header['TAltN'] + 2*header['HAltN'] + n_levels

    (RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF, Elev, Azi, Status,
     TransPow, TransT, RecT, PCT) = [np.empty(n_samples, np.float32) for _ in range(17)]

    SLv = np.zeros((n_samples, n_levels), np.float32)

    if polarization > 0:
        n_dummy += n_levels
        HSpec, ReVHSpec, ImVHSpec = [np.zeros((n_samples, n_levels, n_spectra), np.float32)
                                     for _ in range(3)]
        SLh = np.zeros((n_samples, n_levels), np.float32)
    else:
        HSpec, ReVHSpec, ImVHSpec, SLh = [None]*4

    if compression > 0:
        TotNoisePow = np.zeros((n_samples, n_levels), np.float32)
    else:
        TotNoisePow = None

    if compression == 2:
        RefRat, CorrCoeff, DiffPh = [np.zeros((n_samples, n_levels, n_spectra), np.float32)
                                     for _ in range(3)]
    else:
        RefRat, CorrCoeff, DiffPh = [None]*3

    if anti_alias == 1:
        MinVel = np.zeros((n_samples, n_levels), np.float32)
        AliasMsk = np.zeros((n_samples, n_levels), np.int8)
    else:
        MinVel, AliasMsk = [None]*2

    if compression > 0 and polarization > 0:
        HNoisePow = np.zeros((n_samples, n_levels), np.float32)
    else:
        HNoisePow = None

    if compression == 2 and polarization == 2:
        SLDR, SCorrCoeff = [np.zeros((n_samples, n_levels, n_spectra), np.float32)
                            for _ in range(2)]
        KDP, DiffAtt = [np.zeros((n_samples, n_levels), np.float32) for _ in range(2)]
    else:
        SLDR, SCorrCoeff, KDP, DiffAtt = [None]*4

    if compression == 0:
        for i, n in enumerate(_get_n_samples(header)):
            n_samples_at_each_height[i] = n

    chirp_of_level = np.digitize(range(n_levels), header['RngOffs'])

    for sample in range(n_samples):
        fread(&SampBytes[sample], 4, 1, ptr)
        fread(&Time[sample], 4, 1, ptr)
        _check_timestamp(Time[sample], header)
        fread(&MSec[sample], 4, 1, ptr)
        fread(&QF[sample], 1, 1, ptr)
        fread(&RR[sample], 4, 1, ptr)
        fread(&RelHum[sample], 4, 1, ptr)
        fread(&EnvTemp[sample], 4, 1, ptr)
        fread(&BaroP[sample], 4, 1, ptr)
        fread(&WS[sample], 4, 1, ptr)
        fread(&WD[sample], 4, 1, ptr)
        fread(&DDVolt[sample], 4, 1, ptr)
        fread(&DDTb[sample], 4, 1, ptr)
        fread(&LWP[sample], 4, 1, ptr)
        fread(&PowIF[sample], 4, 1, ptr)
        fread(&Elev[sample], 4, 1, ptr)
        fread(&Azi[sample], 4, 1, ptr)
        fread(&Status[sample], 4, 1, ptr)
        fread(&TransPow[sample], 4, 1, ptr)
        fread(&TransT[sample], 4, 1, ptr)
        fread(&RecT[sample], 4, 1, ptr)
        fread(&PCT[sample], 4, 1, ptr)
        fseek(ptr, n_dummy * 4, SEEK_CUR)  # this chunk contains data (temp profile etc.)
        fread(&SLv[sample, 0], 4, n_levels, ptr)

        if polarization > 0:
            fread(&SLh[sample, 0], 4, n_levels, ptr)

        fread(is_data, 1, n_levels, ptr)

        for alt_ind in range(n_levels):

            if is_data[alt_ind] == 1:

                fseek(ptr, 4, SEEK_CUR)
                n_bins = header['SpecN'][chirp_of_level[alt_ind] - 1]
                bins_to_shift = (n_spectra - n_bins) // 2

                if compression == 0:
                    n_points = n_samples_at_each_height[alt_ind]
                    fread(&TotSpec[sample, alt_ind, bins_to_shift], 4, n_points, ptr)

                    if polarization > 0:
                        fread(&HSpec[sample, alt_ind, bins_to_shift], 4, n_points, ptr)
                        fread(&ReVHSpec[sample, alt_ind, bins_to_shift], 4, n_points, ptr)
                        fread(&ImVHSpec[sample, alt_ind, bins_to_shift], 4, n_points, ptr)

                else:

                    fread(&n_blocks, 1, 1, ptr)
                    fread(&min_ind[0], 2, n_blocks, ptr)
                    fread(&max_ind[0], 2, n_blocks, ptr)

                    for m in range(n_blocks):
                        if min_ind[m] < 0 or max_ind[m] < 0:
                            raise RPGFileError('Invalid data: negative min_ind or max_ind')
                        if min_ind[m] > max_ind[m]:
                            raise RPGFileError('Invalid data: min_ind[m] > max_ind[m]')
                        n_block_points[m] = max_ind[m] - min_ind[m] + 1
                        spec_ind[m] = min_ind[m] + bins_to_shift
                        if spec_ind[m] >= n_spectra:
                            raise RPGFileError('Invalid data: spec_ind[m] > n_spectra')
                        fread(&TotSpec[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)

                    if polarization > 0:
                        for m in range(n_blocks):
                            fread(&HSpec[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        for m in range(n_blocks):
                            fread(&ReVHSpec[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        for m in range(n_blocks):
                            fread(&ImVHSpec[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)

                    if compression == 2:
                        for m in range(n_blocks):
                            fread(&RefRat[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        for m in range(n_blocks):
                            fread(&CorrCoeff[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        for m in range(n_blocks):
                            fread(&DiffPh[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)

                    if compression == 2  and polarization == 2:
                        for m in range(n_blocks):
                            fread(&SLDR[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        for m in range(n_blocks):
                            fread(&SCorrCoeff[sample, alt_ind, spec_ind[m]], 4, n_block_points[m], ptr)
                        fread(&KDP[sample, alt_ind], 4, 1, ptr)
                        fread(&DiffAtt[sample, alt_ind], 4, 1, ptr)

                    fread(&TotNoisePow[sample, alt_ind], 4, 1, ptr)

                    if polarization > 0:
                        fread(&HNoisePow[sample, alt_ind], 4, 1, ptr)

                    if anti_alias == 1:
                        fread(&AliasMsk[sample, alt_ind], 1, 1, ptr)
                        fread(&MinVel[sample, alt_ind], 4, 1, ptr)

    current_position = ftell(ptr)
    fseek(ptr, 0, SEEK_END)
    end_position = ftell(ptr)
    if current_position != end_position:
        raise RPGFileError('File position is not at the end of the file.')

    fclose(ptr)
    free(is_data)
    free(n_samples_at_each_height)

    var_names = locals()
    keys = _get_valid_l0_keys(header)

    return {key: np.asarray(var_names[key]) for key in keys}


def _get_n_samples(header: dict) -> np.ndarray:
    """Finds number of spectral samples at each height."""
    array = np.ones(header['RAltN'], dtype=int)
    sub_arrays = np.split(array, header['RngOffs'][1:])
    for sub_array, scale in zip(sub_arrays, header['SpecN']):
        sub_array *= scale
    return np.concatenate(sub_arrays)


def _get_valid_l0_keys(header: dict) -> list:
    """Controls which variables are provided as output."""

    keys = ['Time', 'MSec', 'QF', 'RR', 'RelHum', 'EnvTemp',
            'BaroP', 'WS', 'WD', 'DDVolt', 'DDTb', 'LWP',
            'PowIF', 'Elev', 'Azi', 'Status', 'TransPow',
            'TransT', 'RecT', 'PCT', 'TotSpec', 'SLv']

    if header['CompEna'] > 0:
        keys += ['TotNoisePow']

    if header['CompEna'] == 2:
        keys += ['RefRat', 'CorrCoeff', 'DiffPh']

    if header['DualPol'] > 0:
        keys += ['HSpec', 'ReVHSpec', 'ImVHSpec', 'SLh']

    if header['CompEna'] > 0 and header['DualPol'] > 0:
        keys += ['HNoisePow']

    if header['CompEna'] == 2 and header['DualPol'] == 2:
        keys += ['SLDR', 'SCorrCoeff', 'KDP', 'DiffAtt']

    if header['AntiAlias'] == 1:
        keys += ['AliasMsk', 'MinVel']

    return keys


def _read_rpg_l1(file_name: bytes, header: dict, version: float) -> dict:
    """Reads RPG LV1 binary file."""

    cdef:
        char* fname = file_name
        FILE *ptr
        int header_length=0, n_samples=0, sample=0, alt_ind=0
        int n_levels = header['RAltN']
        int polarization = header['DualPol']
        char *is_data = <char *> malloc(n_levels * sizeof(char))
        int * n_samples_at_each_height = <int *> malloc(n_levels * sizeof(int))

    ptr = fopen(fname, "rb")
    fseek(ptr, 4, SEEK_CUR)
    fread(&header_length, 4, 1, ptr)
    fseek(ptr, header_length, SEEK_CUR)
    fread(&n_samples, 4, 1, ptr)

    cdef:
        int [:] SampBytes = np.empty(n_samples, np.int32)
        unsigned int [:] Time = np.empty(n_samples, np.uint32)
        int [:] MSec = np.empty(n_samples, np.int32)
        char [:] QF = np.empty(n_samples, np.int8)
        float [:] RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF, RadC
        float [:] Elev, Azi, Status, TransPow, TransT, RecT, PCT
        float [:, :] Ze, MeanVel, SpecWidth, Skewn, Kurt, RefRat, CorrCoeff, DiffPh, SLDR
        float [:, :] SCorrCoeff, KDP, DiffAtt
        int n_dummy = 3 + header['TAltN'] + 2*header['HAltN'] + n_levels

    (RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF, Elev, Azi, Status,
     TransPow, TransT, RecT, PCT, RadC) = [np.empty(n_samples, np.float32) for _ in range(18)]

    (Ze, MeanVel, SpecWidth, Skewn, Kurt, RefRat, CorrCoeff, DiffPh, SLDR, SCorrCoeff,
     KDP, DiffAtt) = [np.zeros((n_samples, n_levels), np.float32) for _ in range(12)]

    if polarization > 0:
        n_dummy += n_levels

    for i, n in enumerate(_get_n_samples(header)):
        n_samples_at_each_height[i] = n

    for sample in range(n_samples):

        fread(&SampBytes[sample], 4, 1, ptr)
        fread(&Time[sample], 4, 1, ptr)
        _check_timestamp(Time[sample], header)
        fread(&MSec[sample], 4, 1, ptr)
        if version > 1.0:
            fread(&QF[sample], 1, 1, ptr)
        fread(&RR[sample], 4, 1, ptr)
        fread(&RelHum[sample], 4, 1, ptr)
        fread(&EnvTemp[sample], 4, 1, ptr)
        fread(&BaroP[sample], 4, 1, ptr)
        fread(&WS[sample], 4, 1, ptr)
        fread(&WD[sample], 4, 1, ptr)
        fread(&DDVolt[sample], 4, 1, ptr)
        fread(&DDTb[sample], 4, 1, ptr)
        fread(&LWP[sample], 4, 1, ptr)
        fread(&PowIF[sample], 4, 1, ptr)
        fread(&Elev[sample], 4, 1, ptr)
        fread(&Azi[sample], 4, 1, ptr)
        fread(&Status[sample], 4, 1, ptr)
        fread(&TransPow[sample], 4, 1, ptr)
        fread(&TransT[sample], 4, 1, ptr)
        fread(&RecT[sample], 4, 1, ptr)
        fread(&PCT[sample], 4, 1, ptr)
        if version == 1.0:
            fseek(ptr, 3 * 4, SEEK_CUR)
            fread(&RadC[sample], 4, 1, ptr)
            fseek(ptr, header["SequN"] * 4, SEEK_CUR)
        else:
            fseek(ptr, n_dummy * 4, SEEK_CUR)  # this chunk contains data (temp profile etc.)

        fread(is_data, 1, n_levels, ptr)

        for alt_ind in range(n_levels):

            if is_data[alt_ind] == 1:
                fread(&Ze[sample, alt_ind], 4, 1, ptr)
                fread(&MeanVel[sample, alt_ind], 4, 1, ptr)
                fread(&SpecWidth[sample, alt_ind], 4, 1, ptr)
                fread(&Skewn[sample, alt_ind], 4, 1, ptr)
                fread(&Kurt[sample, alt_ind], 4, 1, ptr)
                if version == 1.0:
                    fseek(ptr, n_samples_at_each_height[alt_ind] * 4, SEEK_CUR)
                else:
                    if polarization > 0:
                        fread(&RefRat[sample, alt_ind], 4, 1, ptr)
                        fread(&CorrCoeff[sample, alt_ind], 4, 1, ptr)
                        fread(&DiffPh[sample, alt_ind], 4, 1, ptr)

                    if  polarization == 2:
                        fseek(ptr, 4, SEEK_CUR)
                        fread(&SLDR[sample, alt_ind], 4, 1, ptr)
                        fread(&SCorrCoeff[sample, alt_ind], 4, 1, ptr)
                        fread(&KDP[sample, alt_ind], 4, 1, ptr)
                        fread(&DiffAtt[sample, alt_ind], 4, 1, ptr)


    current_position = ftell(ptr)
    fseek(ptr, 0, SEEK_END)
    end_position = ftell(ptr)
    if current_position != end_position:
        raise RPGFileError('File position is not at the end of the file.')

    fclose(ptr)
    free(is_data)

    var_names = locals()
    keys = _get_valid_l1_keys(header)

    return {key: np.asarray(var_names[key]) for key in keys}


def _get_valid_l1_keys(header: dict) -> list:
    """Controls which variables are provided as output."""

    keys = ['Time', 'MSec', 'QF', 'RR', 'RelHum', 'EnvTemp',
            'BaroP', 'WS', 'WD', 'DDVolt', 'DDTb', 'LWP',
            'PowIF', 'Elev', 'Azi', 'Status', 'TransPow',
            'TransT', 'RecT', 'PCT', 'Ze', 'MeanVel',
            'SpecWidth', 'Skewn', 'Kurt']

    if header['DualPol']:
        keys += ['RefRat', 'CorrCoeff', 'DiffPh']

    if header['DualPol'] == 2:
        keys += ['SLDR', 'SCorrCoeff', 'KDP', 'DiffAtt']

    return keys


def _check_timestamp(timestamp: int, header: dict):
    """Checks if timestamp is within the expected range."""
    try:
        if not (header['StartTime'] <= timestamp <= header['StopTime']):
            raise RPGFileError(f'Timestamp {timestamp} is outside the expected range '
            f'[{header["StartTime"]}, {header["StopTime"]}].')
    except KeyError:
        return
