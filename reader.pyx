"""RPG cloud radar binary reader in Cython."""
from libc.stdio cimport *
import numpy as np
import rpg_header
import numpy as np

DEF MAX_N_SPECTRAL_BLOCKS = 100
DEF MAX_ALTITUDES = 1500

def read_bytes(str file_name, header):

    filename_byte_string = file_name.encode("UTF-8")
    cdef:
        char* fname = filename_byte_string
        FILE *ptr
        int ret, header_length, n_samples, sample, j, n_bytes, n, m, alt_ind
        int level, version
        char dummy_char, n_blocks
        float value
        int n_spectra = max(header['n_spectral_samples'])
        int n_levels = header['_n_range_levels']
        int compression = header['compression']
        int polarization = header['dual_polarization']
        int anti_alias = header['anti_alias']
        char is_data[MAX_ALTITUDES]
        int n_samples_at_each_height[MAX_ALTITUDES]
        short int min_ind[MAX_N_SPECTRAL_BLOCKS]
        short int max_ind[MAX_N_SPECTRAL_BLOCKS]

    level, version = rpg_header.get_rpg_file_type(header)

    ptr = fopen(fname, "rb")

    fseek(ptr, 4, SEEK_CUR)
    ret = fread(&header_length, 4, 1, ptr)
    fseek(ptr, header_length, SEEK_CUR)
    ret = fread(&n_samples, 4, 1, ptr)

    cdef int [:] SampBytes = np.empty(n_samples, np.int32)
    cdef unsigned int [:] Time = np.empty(n_samples, np.uint32)
    cdef int [:] MSec = np.empty(n_samples, np.int32)
    cdef int [:] QF = np.empty(n_samples, np.int32)
    cdef float [:] RR = np.empty(n_samples, np.float32)
    cdef float [:] RelHum = np.empty(n_samples, np.float32)
    cdef float [:] EnvTemp = np.empty(n_samples, np.float32)
    cdef float [:] BaroP = np.empty(n_samples, np.float32)
    cdef float [:] WS = np.empty(n_samples, np.float32)
    cdef float [:] WD = np.empty(n_samples, np.float32)
    cdef float [:] DDVolt = np.empty(n_samples, np.float32)
    cdef float [:] DDTb = np.empty(n_samples, np.float32)
    cdef float [:] LWP = np.empty(n_samples, np.float32)
    cdef float [:] PowIF = np.empty(n_samples, np.float32)
    cdef float [:] Elev = np.empty(n_samples, np.float32)
    cdef float [:] Azi = np.empty(n_samples, np.float32)
    cdef float [:] Status = np.empty(n_samples, np.float32)
    cdef float [:] TransPow = np.empty(n_samples, np.float32)
    cdef float [:] TransT = np.empty(n_samples, np.float32)
    cdef float [:] RecT = np.empty(n_samples, np.float32)
    cdef float [:] PCT = np.empty(n_samples, np.float32)
    cdef float [:, :, :] TotSpec = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] HSpec = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] ReVHSpec = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] ImVHSpec = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] RefRat = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] CorrCoeff = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] DiffPh = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] SLDR = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :, :] SCorrCoeff = np.zeros((n_samples, n_levels, n_spectra), np.float32)
    cdef float [:, :] KDP = np.zeros((n_samples, n_levels), np.float32)
    cdef float [:, :] DiffAtt = np.zeros((n_samples, n_levels), np.float32)
    cdef float [:, :] TotNoisePow = np.zeros((n_samples, n_levels), np.float32)
    cdef float [:, :] HNoisePow = np.zeros((n_samples, n_levels), np.float32)
    #cdef int [:, :] AliasMsk = np.zeros((n_samples, n_levels), np.int32)
    cdef float [:, :] MinVel = np.zeros((n_samples, n_levels), np.float32)

    cdef int n_dummy = header['_n_temperature_levels'] + 2*header['_n_humidity_levels'] + 2*n_levels
    if level == 0 and polarization > 0:
        n_dummy += 2*n_levels

    if compression == 0:
        temp = _get_n_samples(header)
        for i in range(len(temp)):
            n_samples_at_each_height[i] = temp[i]

    # Loop over time
    for sample in range(n_samples):

        ret = fread(&SampBytes[sample], 4, 1, ptr)
        ret = fread(&Time[sample], 4, 1, ptr)
        ret = fread(&MSec[sample], 4, 1, ptr)
        #ret = fread(&QF[sample], 1, 1, ptr)
        fseek(ptr, 1, SEEK_CUR)
        ret = fread(&RR[sample], 4, 1, ptr)
        ret = fread(&RelHum[sample], 4, 1, ptr)
        ret = fread(&EnvTemp[sample], 4, 1, ptr)
        ret = fread(&BaroP[sample], 4, 1, ptr)
        ret = fread(&WS[sample], 4, 1, ptr)
        ret = fread(&WD[sample], 4, 1, ptr)
        ret = fread(&DDVolt[sample], 4, 1, ptr)
        ret = fread(&DDTb[sample], 4, 1, ptr)
        ret = fread(&LWP[sample], 4, 1, ptr)
        ret = fread(&PowIF[sample], 4, 1, ptr)
        ret = fread(&Elev[sample], 4, 1, ptr)
        ret = fread(&Azi[sample], 4, 1, ptr)
        ret = fread(&Status[sample], 4, 1, ptr)
        ret = fread(&TransPow[sample], 4, 1, ptr)
        ret = fread(&TransT[sample], 4, 1, ptr)
        ret = fread(&RecT[sample], 4, 1, ptr)
        ret = fread(&PCT[sample], 4, 1, ptr)
        fseek(ptr, (3 + n_dummy)*4, SEEK_CUR)

        # Read altitudes where we actually have some data
        #ret = fread(is_data, 1, n_levels, ptr)
        for i in range(n_levels):
            ret = fread(&is_data[i], 1, 1, ptr)

        for alt_ind in range(n_levels):

            if is_data[alt_ind] == 1:
                
                ret = fread(&n_bytes, 4, 1, ptr)

                if compression == 0:

                    for n in range(n_samples_at_each_height[alt_ind]):
                        ret = fread(&TotSpec[sample, alt_ind, n], 4, 1, ptr)

                    if polarization > 0:
                        for n in range(n_samples_at_each_height[alt_ind]):
                            ret = fread(&HSpec[sample, alt_ind, n], 4, 1, ptr)
                        for n in range(n_samples_at_each_height[alt_ind]):
                            ret = fread(&ReVHSpec[sample, alt_ind, n], 4, 1, ptr)
                        for n in range(n_samples_at_each_height[alt_ind]):
                            ret = fread(&ImVHSpec[sample, alt_ind, n], 4, 1, ptr)

                else:

                    ret = fread(&n_blocks, 1, 1, ptr)

                    for m in range(n_blocks):
                        ret = fread(&min_ind[m], 2, 1, ptr)
                    for m in range(n_blocks):
                        ret = fread(&max_ind[m], 2, 1, ptr)

                    for m in range(n_blocks):
                        for n in range(min_ind[m], max_ind[m]+1):
                            ret = fread(&TotSpec[sample, alt_ind, n], 4, 1, ptr)

                        if polarization > 0:
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&HSpec[sample, alt_ind, n], 4, 1, ptr)
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&ReVHSpec[sample, alt_ind, n], 4, 1, ptr)
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&ImVHSpec[sample, alt_ind, n], 4, 1, ptr)

                        if compression == 2:
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&RefRat[sample, alt_ind, n], 4, 1, ptr)
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&CorrCoeff[sample, alt_ind, n], 4, 1, ptr)
                            for n in range(min_ind[m], max_ind[m]+1):
                                ret = fread(&DiffPh[sample, alt_ind, n], 4, 1, ptr)

                            if polarization == 2:
                                for n in range(min_ind[m], max_ind[m]+1):
                                    ret = fread(&SLDR[sample, alt_ind, n], 4, 1, ptr)
                                for n in range(min_ind[m], max_ind[m]+1):
                                    ret = fread(&SCorrCoeff[sample, alt_ind, n], 4, 1, ptr)

                    if polarization == 2 and compression == 2:
                        ret = fread(&KDP[sample, alt_ind], 4, 1, ptr)
                        ret = fread(&DiffAtt[sample, alt_ind], 4, 1, ptr)

                    ret = fread(&TotNoisePow[sample, alt_ind], 4, 1, ptr)

                    if polarization > 0:
                        ret = fread(&HNoisePow[sample, alt_ind], 4, 1, ptr)
                        
                    if anti_alias == 1:
                        #ret = fread(&AliasMsk[sample, alt_ind], 1, 1, ptr)
                        fseek(ptr, 1, SEEK_CUR)
                        ret = fread(&MinVel[sample, alt_ind], 4, 1, ptr)


    fclose(ptr)

    return {'TotSpec': np.asarray(TotSpec),
            'HSpec': np.asarray(HSpec),
            'ReVHSpec': np.asarray(ReVHSpec),
            'ImVHSpec': np.asarray(ImVHSpec),
            }


def _get_n_samples(header):
    """Finds number of spectral samples at each height."""
    array = np.ones(header['_n_range_levels'], dtype=int)
    sub_arrays = np.split(array, header['chirp_start_indices'][1:])
    sub_arrays *= header['n_spectral_samples']
    return np.concatenate(sub_arrays)
