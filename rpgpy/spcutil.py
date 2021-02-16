from typing import Dict, List, Tuple

import numpy as np
from numba import jit


def spectra2moments(LV0data: Dict, LV0meta: Dict, spec_var: str='TotSpec'):
    """
    This routine calculates the radar moments: reflectivity, mean Doppler velocity, spectrum width, skewness and
    kurtosis from compressed level 0 spectrum files (NoiseFactor > 0) of the 94 GHz RPG cloud radar.

    Args:
        LV0data: lv0 nD variables
        LV0meta: lv0 meta data

    Return:
        container_dict: dictionary of larda containers, including larda container for Ze, VEL, sw, skew, kurt

    """
    # initialize variables:
    n_ts, n_rg = LV0data[spec_var].shape[:2]
    moments = np.full((n_ts, n_rg, 5), np.nan)

    spec_lin = LV0data[spec_var].copy()
    mask = spec_lin <= 0.0
    spec_lin[mask] = 0.0

    # combine the mask for "contains signal" with "signal has more than 1 spectral line"
    mask2D = np.all(mask, axis=2)
    ranges = np.append(LV0meta['RngOffs'], LV0meta['RAltN'])

    for iC in range(LV0meta['SequN']):
        Dopp_res = np.mean(np.diff(LV0meta['velocity_vectors'][iC]))

        for iR in range(ranges[iC], ranges[iC + 1]):
            for iT in range(n_ts):
                if mask2D[iT, iR]: continue
                _, (lb, rb) = find_peak_edges(spec_lin[iT, iR, :])
                moments[iT, iR, :] = radar_moment_calculation(
                    spec_lin[iT, iR, lb:rb],
                    LV0meta['velocity_vectors'][iC][lb:rb]
                )

        # shift mean Doppler velocity by half a bin
        moments[:, ranges[iC]:ranges[iC + 1], 1] -= Dopp_res / 2.0

    # create the mask where invalid values have been encountered
    invalid_mask = np.full((n_ts, n_rg), True)
    invalid_mask[np.where(moments[:, :, 0] > 0.0)] = False

    moments = {var: moments[:, :, i] for i, var in enumerate(['Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'])}

    for mom in moments.keys():
        moments[mom][invalid_mask] = -999.0

    return moments


@jit(nopython=True, fastmath=True)
def radar_moment_calculation(signal: np.array, vel_bins: np.array) -> np.array:
    """
    Calculation of radar moments: reflectivity, mean Doppler velocity, spectral width,
        skewness, and kurtosis of one Doppler spectrum. Optimized for the use of Numba.

    Note:
        Divide the signal_sum by 2 because vertical and horizontal channel are added.
        Subtract half of of the Doppler resolution from mean Doppler velocity, because

    Args:
        - signal: detected signal from a Doppler spectrum
        - vel_bins: extracted velocity bins of the signal (same length as signal)

    Returns:
        dict containing

            - Ze_lin: reflectivity (0.Mom) over range of velocity bins [mm6/m3]
            - VEL: mean velocity (1.Mom) over range of velocity bins [m/s]
            - sw: spectrum width (2.Mom) over range of velocity bins [m/s]
            - skew: skewness (3.Mom) over range of velocity bins
            - kurt: kurtosis (4.Mom) over range of velocity bins
    """

    signal_sum = np.sum(signal)  # linear full spectrum Ze [mm^6/m^3], scalar
    Ze_lin = signal_sum / 2.0
    pwr_nrm = signal / signal_sum  # determine normalized power (NOT normalized by Vdop bins)

    VEL = np.sum(vel_bins * pwr_nrm)
    vel_diff = vel_bins - VEL
    vel_diff2 = vel_diff * vel_diff
    sw = np.sqrt(np.abs(np.sum(pwr_nrm * vel_diff2)))
    sw2 = sw * sw
    skew = np.sum(pwr_nrm * vel_diff * vel_diff2 / (sw * sw2))
    kurt = np.sum(pwr_nrm * vel_diff2 * vel_diff2 / (sw2 * sw2))

    return np.array((Ze_lin, VEL, sw, skew, kurt), dtype=float())


@jit(nopython=True, fastmath=True)
def find_peak_edges(signal: np.array, threshold: float = -1, imaxima: int = -1) -> Tuple[float, List[int]]:
    """Returns the indices of left and right edge of the main signal peak in a Doppler spectra.

    Args:
        signal: 1D array Doppler spectra
        threshold (optional): noise threshold
        imaxima (optional): index of signal maximum

    Returns:
        threshold, [index_left, index_right]: noise threshold & indices of signal minimum/maximum velocity
    """
    len_sig = len(signal)
    index_left, index_right = 0, len_sig
    if threshold < 0: threshold = np.min(signal)
    if imaxima < 0: imaxima = np.argmax(signal)

    for ispec in range(imaxima, len_sig):
        if signal[ispec] > threshold: continue
        index_right = ispec
        break

    for ispec in range(imaxima, -1, -1):
        if signal[ispec] > threshold: continue
        index_left = ispec + 1  # the +1 is important, otherwise a fill_value will corrupt the numba code
        break

    return threshold, [index_left, index_right]



def replace_fill_value(data: np.array, newfill: np.array) -> np.array:
    """Replaces the fill value of an spectrum by another value.
    Args:
        data: 3D spectrum array (time, range, velocity)
        newfill: 2D new fill values for 3rd dimension (velocity)

    Return:
        var: spectrum with new fill values
    """

    n_ts, n_rg, _ = data.shape
    var = data.copy()
    masked = np.all(data <= 0.0, axis=2)

    for iT in range(n_ts):
        for iR in range(n_rg):
            if masked[iT, iR]:
                var[iT, iR, :] = newfill[iT, iR]
            else:
                var[iT, iR, var[iT, iR, :] <= 0.0] = newfill[iT, iR]
    return var

