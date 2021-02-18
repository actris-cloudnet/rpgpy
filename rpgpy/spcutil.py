from typing import Dict, Tuple, Optional
import numpy as np
from numba import jit


def spectra2moments(LV0data: Dict, LV0meta: Dict, spec_var: Optional[str] = 'TotSpec', fill_value: Optional[float] = -999.0):
    """
    This routine calculates the radar moments: reflectivity, mean Doppler velocity, spectrum width, skewness and
    kurtosis from compressed level 0 spectrum files (NoiseFactor > 0) of the 94 GHz RPG cloud radar. Considering
    only the largest peak.

    Args:
        LV0data: lv0 nD variables
        LV0meta: lv0 meta data
        spec_var: name of spectrum variable
        fill_value: clear sky fill value

    Return:
        dict: dictionary with keys: 'Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'

    """
    # initialize variables:
    n_time, n_range, _ = LV0data[spec_var].shape
    moments = np.full((n_time, n_range, 5), np.nan)

    spec_lin = LV0data[spec_var].copy()
    mask = ~(spec_lin > 0)
    spec_lin[mask] = 0.0

    # combine the mask for "contains signal" with "signal has more than 1 spectral line"
    no_signal = np.all(mask, axis=2)
    ranges = np.append(LV0meta['RngOffs'], LV0meta['RAltN'])

    for ind_chirp in range(LV0meta['SequN']):
        Dopp_res = np.mean(np.diff(LV0meta['velocity_vectors'][ind_chirp]))

        for ind_range in range(ranges[ind_chirp], ranges[ind_chirp + 1]):
            for ind_time in range(n_time):
                if no_signal[ind_time, ind_range]:
                    continue
                edge_left, edge_right = find_peak_edges(spec_lin[ind_time, ind_range, :])
                moments[ind_time, ind_range, :] = radar_moment_calculation(
                    spec_lin[ind_time, ind_range, edge_left:edge_right],
                    LV0meta['velocity_vectors'][ind_chirp][edge_left:edge_right]
                )

        # shift mean Doppler velocity by half a bin
        moments[:, ranges[ind_chirp]:ranges[ind_chirp + 1], 1] -= Dopp_res / 2.0

    # create the mask where invalid values have been encountered
    invalid_mask = np.full((n_time, n_range), True)
    invalid_mask[moments[:, :, 0] > 0.0] = False

    moments = {var: moments[:, :, i] for i, var in enumerate(['Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'])}

    for mom in moments.keys():
        moments[mom][invalid_mask] = fill_value

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
        array containing

            - Ze_lin: reflectivity (0.Mom) over range of velocity bins [mm6/m3]
            - VEL: mean velocity (1.Mom) over range of velocity bins [m/s]
            - sw: spectrum width (2.Mom) over range of velocity bins [m/s]
            - skew: skewness (3.Mom) over range of velocity bins
            - kurt: kurtosis (4.Mom) over range of velocity bins

    TODO:
        Unit test
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

    return np.array((Ze_lin, VEL, sw, skew, kurt), dtype=np.float32)


@jit(nopython=True, fastmath=True)
def find_peak_edges(signal: np.array) -> Tuple[int, int]:
    """Returns the indices of left and right edge of the main signal peak in a Doppler spectra.

    Args:
        signal: 1D array Doppler spectra

    Returns:
        edge_left, edge_right: indices of minimum/maximum velocity of the main peak

    """
    len_sig = len(signal)
    edge_left, edge_right = 0, len_sig
    threshold = np.min(signal)
    imax = np.argmax(signal)

    for ispec in range(imax, len_sig):
        if signal[ispec] > threshold:
            continue
        edge_right = ispec
        break

    for ispec in range(imax, -1, -1):
        if signal[ispec] > threshold:
            continue
        edge_left = ispec + 1  # the +1 is important, otherwise a fill_value will corrupt the numba code
        break

    return edge_left, edge_right

