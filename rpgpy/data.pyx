"""RPG cloud radar binary reader in Cython."""
from libc.stdio cimport *
from libc.stdlib cimport malloc, free
import numpy as np
from rpgpy import utils, header

DEF MAX_N_SPECTRAL_BLOCKS = 100


def read_rpg(file_name, rpg_names=True):
    """ Reads RPG Level 1 / Level 0 binary file.

    Args:
        file_name (str): File name.
        rpg_names (bool, optional): If True, uses RPG naming scheme 
            for the returned data dict. Otherwise uses custom names. 
            Default is True.

    Returns:
        tuple: 2-element tuple containing header (dict) and data (dict).

    """
    file_header, _ = header.read_rpg_header(file_name)
    level, version = utils.get_rpg_file_type(file_header)
    fun = _read_rpg_l0 if level == 0 else _read_rpg_l1
    return file_header, fun(file_name, file_header, rpg_names)


def _read_rpg_l0(file_name, header, rpg_names):
    """Reads RPG LV0 binary file."""
    
    filename_byte_string = file_name.encode("UTF-8")
    cdef:
        char* fname = filename_byte_string
        FILE *ptr
        int header_length=0, n_samples=0, sample=0, j=0, n=0, m=0
        int alt_ind=0, n_points=0, ind1=0
        char n_blocks
        int n_spectra = max(header['n_spectral_samples'])
        int n_levels = header['_n_range_levels']
        int compression = header['compression']
        int polarization = header['dual_polarization']
        int anti_alias = header['anti_alias']
        short int min_ind[MAX_N_SPECTRAL_BLOCKS]
        short int max_ind[MAX_N_SPECTRAL_BLOCKS]
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
        float [:, :] KDP, DiffAtt, TotNoisePow, HNoisePow, MinVel
        char [:, :] AliasMsk        
        int n_dummy = 3 + header['_n_temperature_levels'] + 2*header['_n_humidity_levels'] + 2*n_levels

    (RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF, Elev, Azi, Status,
     TransPow, TransT, RecT, PCT) = [np.empty(n_samples, np.float32) for _ in range(17)]
        
    if polarization > 0:
        n_dummy += 2*n_levels
        HSpec, ReVHSpec, ImVHSpec = [np.zeros((n_samples, n_levels, n_spectra), np.float32) for _ in range(3)]
    else:
        HSpec, ReVHSpec, ImVHSpec = [None]*3

    if compression > 0:
        TotNoisePow = np.zeros((n_samples, n_levels), np.float32)
    else:
        TotNoisePow = None
        
    if compression == 2:
        RefRat, CorrCoeff, DiffPh = [np.zeros((n_samples, n_levels, n_spectra), np.float32) for _ in range(3)]
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
        SLDR, SCorrCoeff = [np.zeros((n_samples, n_levels, n_spectra), np.float32) for _ in range(2)]
        KDP, DiffAtt = [np.zeros((n_samples, n_levels), np.float32) for _ in range(2)]
    else:
        SLDR, SCorrCoeff, KDP, DiffAtt = [None]*4
    
    if compression == 0:
        for i, n in enumerate(_get_n_samples(header)):
            n_samples_at_each_height[i] = n

    for sample in range(n_samples):

        fread(&SampBytes[sample], 4, 1, ptr)
        fread(&Time[sample], 4, 1, ptr)
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
        fseek(ptr, n_dummy * 4, SEEK_CUR)
        fread(is_data, 1, n_levels, ptr)

        for alt_ind in range(n_levels):

            if is_data[alt_ind] == 1:                
                fseek(ptr, 4, SEEK_CUR)

                if compression == 0:

                    n_points = n_samples_at_each_height[alt_ind]
                    fread(&TotSpec[sample, alt_ind, 0], 4, n_points, ptr)
                    
                    if polarization > 0:
                        fread(&HSpec[sample, alt_ind, 0], 4, n_points, ptr)
                        fread(&ReVHSpec[sample, alt_ind, 0], 4, n_points, ptr)
                        fread(&ImVHSpec[sample, alt_ind, 0], 4, n_points, ptr)

                else:
                    
                    fread(&n_blocks, 1, 1, ptr)
                    fread(&min_ind[0], 2, n_blocks, ptr)
                    fread(&max_ind[0], 2, n_blocks, ptr)
                    
                    for m in range(n_blocks):

                        ind1 = min_ind[m]
                        n_points = max_ind[m]-ind1+1

                        fread(&TotSpec[sample, alt_ind, ind1], 4, n_points, ptr)
                        
                        if polarization > 0:
                            fread(&HSpec[sample, alt_ind, ind1], 4, n_points, ptr)
                            fread(&ReVHSpec[sample, alt_ind, ind1], 4, n_points, ptr)
                            fread(&ImVHSpec[sample, alt_ind, ind1], 4, n_points, ptr)

                        if compression == 2:
                            fread(&RefRat[sample, alt_ind, ind1], 4, n_points, ptr)
                            fread(&CorrCoeff[sample, alt_ind, ind1], 4, n_points, ptr)
                            fread(&DiffPh[sample, alt_ind, ind1], 4, n_points, ptr)

                        if compression == 2  and polarization == 2:
                            fread(&SLDR[sample, alt_ind, ind1], 4, n_points, ptr)
                            fread(&SCorrCoeff[sample, alt_ind, ind1], 4, n_points, ptr)

                    if compression == 2 and polarization == 2:
                        fread(&KDP[sample, alt_ind], 4, 1, ptr)
                        fread(&DiffAtt[sample, alt_ind], 4, 1, ptr)

                    fread(&TotNoisePow[sample, alt_ind], 4, 1, ptr)

                    if polarization > 0:
                        fread(&HNoisePow[sample, alt_ind], 4, 1, ptr)
                        
                    if anti_alias == 1:
                        fread(&AliasMsk[sample, alt_ind], 1, 1, ptr)
                        fread(&MinVel[sample, alt_ind], 4, 1, ptr)

    fclose(ptr)
    free(is_data)
    free(n_samples_at_each_height)

    # If big-endian machine: need to swap bytes..?

    var_names = locals()
    keys = _get_valid_l0_keys(header)

    if rpg_names:
        return {key: np.asarray(var_names[key]) for key in keys}
    return {OUTPUT_KEYS[key]: np.asarray(var_names[key]) for key in keys}


def _get_n_samples(header):
    """Finds number of spectral samples at each height."""
    array = np.ones(header['_n_range_levels'], dtype=int)
    sub_arrays = np.split(array, header['chirp_start_indices'][1:])
    sub_arrays *= header['n_spectral_samples']
    return np.concatenate(sub_arrays)


def _get_valid_l0_keys(header):
    """Controls which variables our provided as output."""
    
    keys = ['Time', 'MSec', 'QF', 'RR', 'RelHum', 'EnvTemp',
            'BaroP', 'WS', 'WD', 'DDVolt', 'DDTb', 'LWP',
            'PowIF', 'Elev', 'Azi', 'Status', 'TransPow',
            'TransT', 'RecT', 'PCT', 'TotSpec']

    if header['compression'] > 0:
        keys += ['TotNoisePow']

    if header['compression'] == 2:
        keys += ['RefRat', 'CorrCoeff', 'DiffPh']
        
    if header['dual_polarization'] > 0:
        keys += ['HSpec', 'ReVHSpec', 'ImVHSpec']

    if header['compression'] > 0 and header['dual_polarization'] > 0:
        keys += ['HNoisePow']
        
    if header['compression'] == 2 and header['dual_polarization'] == 2:
        keys += ['SLDR', 'SCorrCoeff', 'KDP', 'DiffAtt']

    if header['anti_alias'] == 1:
        keys += ['AliasMsk', 'MinVel']
        
    return keys


def _read_rpg_l1(file_name, header, rpg_names):
    """Reads RPG LV1 binary file."""
    
    filename_byte_string = file_name.encode("UTF-8")
    cdef:
        char* fname = filename_byte_string
        FILE *ptr
        int header_length=0, n_samples=0, sample=0, alt_ind=0
        int n_levels = header['_n_range_levels']
        int polarization = header['dual_polarization']
        char *is_data = <char *> malloc(n_levels * sizeof(char))

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
        float [:] RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF
        float [:] Elev, Azi, Status, TransPow, TransT, RecT, PCT
        float [:, :] Ze, MeanVel, SpecWidth, Skewn, Kurt, RefRat, CorrCoeff, DiffPh, SLDR, SCorrCoeff, KDP, DiffAtt
        int n_dummy = 3 + header['_n_temperature_levels'] + 2*header['_n_humidity_levels'] + n_levels

    (RR, RelHum, EnvTemp, BaroP, WS, WD, DDVolt, DDTb, LWP, PowIF, Elev, Azi, Status,
     TransPow, TransT, RecT, PCT) = [np.empty(n_samples, np.float32) for _ in range(17)]
        
    (Ze, MeanVel, SpecWidth, Skewn, Kurt, RefRat, CorrCoeff, DiffPh, SLDR, SCorrCoeff,
     KDP, DiffAtt) = [np.zeros((n_samples, n_levels), np.float32) for _ in range(12)]
        
    if polarization > 0:
        n_dummy += n_levels

    for sample in range(n_samples):

        fread(&SampBytes[sample], 4, 1, ptr)
        fread(&Time[sample], 4, 1, ptr)
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
        fseek(ptr, n_dummy * 4, SEEK_CUR)
        fread(is_data, 1, n_levels, ptr)

        for alt_ind in range(n_levels):

            if is_data[alt_ind] == 1:
                fread(&Ze[sample, alt_ind], 4, 1, ptr)
                fread(&MeanVel[sample, alt_ind], 4, 1, ptr)
                fread(&SpecWidth[sample, alt_ind], 4, 1, ptr)
                fread(&Skewn[sample, alt_ind], 4, 1, ptr)
                fread(&Kurt[sample, alt_ind], 4, 1, ptr)

                if polarization > 0:
                    fread(&RefRat[sample, alt_ind], 4, 1, ptr)
                    fread(&CorrCoeff[sample, alt_ind], 4, 1, ptr)
                    fread(&DiffPh[sample, alt_ind], 4, 1, ptr)

                if polarization == 2:
                    fseek(ptr, 1, SEEK_CUR)
                    fread(&SLDR[sample, alt_ind], 4, 1, ptr)
                    fread(&SCorrCoeff[sample, alt_ind], 4, 1, ptr)
                    fread(&KDP[sample, alt_ind], 4, 1, ptr)
                    fread(&DiffAtt[sample, alt_ind], 4, 1, ptr)

    fclose(ptr)
    free(is_data)

    var_names = locals()
    keys = _get_valid_l1_keys(header)

    if rpg_names:
        return {key: np.asarray(var_names[key]) for key in keys}
    return {OUTPUT_KEYS[key]: np.asarray(var_names[key]) for key in keys}


def _get_valid_l1_keys(header):
    """Controls which variables our provided as output."""
    
    keys = ['Time', 'MSec', 'QF', 'RR', 'RelHum', 'EnvTemp',
            'BaroP', 'WS', 'WD', 'DDVolt', 'DDTb', 'LWP',
            'PowIF', 'Elev', 'Azi', 'Status', 'TransPow',
            'TransT', 'RecT', 'PCT', 'Ze', 'MeanVel',
            'SpecWidth', 'Skewn', 'Kurt']

    if header['dual_polarization']:
        keys += ['RefRat', 'CorrCoeff', 'DiffPh']

    if header['dual_polarization'] == 2:
        keys += ['SLDR', 'SCorrCoeff', 'KDP', 'DiffAtt']

    return keys


OUTPUT_KEYS = {
    'Time': 'time',
    'MSec': 'time_ms',
    'QF': 'quality_flag',
    'RR': 'rain_rate',
    'RelHum': 'relative_humidity',
    'EnvTemp': 'temperature',
    'BaroP': 'pressure',
    'WS': 'wind_speed',
    'WD': 'wind_direction',
    'DDVolt': 'voltage',
    'DDTb': 'brightness_temperature',
    'TransPow': 'transmitted_power',
    'TransT': 'transmitter_temperature',
    'RecT': 'receiver_temperature',
    'PCT': 'pc_temperature',
    'LWP': 'lwp',
    'Elev': 'elevation',
    'Azi': 'azimuth',
    'Status': 'status_flag',
    'TotSpec': 'doppler_spectrum',
    'HSpec': 'doppler_spectrum_h',
    'ReVHSpec': 'covariance_spectrum_re',
    'ImVHSpec': 'covariance_spectrum_im',
    'RefRat': 'differential_reflectivity',
    'DiffPh': 'differential_phase',
    'SLDR': 'ldr_slanted',
    'CorrCoeff': 'correlation_coefficient',
    'SCorrCoeff': 'correlation_coefficient_slanted',
    'KDP': 'differential_phase_shift',
    'DiffAtt': 'differential_attenuation',
    'TotNoisePow': 'integrated_noise',
    'HNoisePow': 'integrated_noise_h',
    'AliasMsk': 'anti_alias_correction',
    'MinVel': 'minimum_velocity',
    'PowIF': 'IF_power',
    'Ze': 'reflectivity',
    'MeanVel': 'velocity',
    'SpecWidth': 'width',
    'Skewn': 'skewness',
    'Kurt': 'kurtosis',
}
