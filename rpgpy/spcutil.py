from typing import Tuple, Optional
import numpy as np
from numba import jit


def spectra2moments(data: dict,
                    header: dict,
                    spec_var: Optional[str] = 'TotSpec',
                    fill_value: Optional[float] = -999.0,
                    n_points_min: Optional[int] = 4) -> dict:
    """
    This routine calculates the radar moments: reflectivity, mean Doppler velocity, spectrum width,
    skewness and kurtosis from compressed level 0 spectrum files (NoiseFactor > 0)
    of the 94 GHz RPG cloud radar. Considering only the largest peak.

    Args:
        data (dict): lv0 nD variables.
        header (dict): lv0 meta data.
        spec_var (str, optional): name of spectrum variable. Possible names are 'TotSpec', 'VSpec',
            and 'HSpec'. Default is 'TotSpec'.
        fill_value (float, optional): clear sky fill value. Default is -999.0.
        n_points_min (int, optional): Minimum number of points in spectral line. Default is 4.

    Returns:
        dict: dictionary with keys: 'Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'.

    Examples:
        >>> from rpgpy import read_rpg, spectra2moments
        >>> header, data = read_rpg('rpg-fmcw-94-file.LV0')
        >>> moments = spectra2moments(data, header)

    """
    spectra = data[spec_var]
    n_time, n_range, _ = spectra.shape
    moments = np.full((n_time, n_range, 5), np.nan)
    no_signal = np.all(spectra == 0, axis=2)
    ranges = np.append(header['RngOffs'], header['RAltN'])

    for ind_chirp in range(header['SequN']):
        dopp_res = np.mean(np.diff(header['velocity_vectors'][ind_chirp]))
        for ind_range in range(ranges[ind_chirp], ranges[ind_chirp + 1]):
            for ind_time in range(n_time):
                if no_signal[ind_time, ind_range]:
                    continue
                edge_left, edge_right = find_peak_edges(spectra[ind_time, ind_range, :])
                if (edge_right - edge_left) < n_points_min:
                    no_signal[ind_time, ind_range] = True
                    continue
                moments[ind_time, ind_range, :] = radar_moment_calculation(
                    spectra[ind_time, ind_range, edge_left:edge_right],
                    header['velocity_vectors'][ind_chirp][edge_left:edge_right])

        # shift mean Doppler velocity by half a bin
        moments[:, ranges[ind_chirp]:ranges[ind_chirp + 1], 1] -= dopp_res / 2.0

    moments = {key: moments[:, :, i] for i, key in enumerate(['Ze', 'MeanVel', 'SpecWidth',
                                                              'Skewn', 'Kurt'])}
    for key in moments.keys():
        moments[key][no_signal] = fill_value

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
        signal (np.array): detected signal from a Doppler spectrum
        vel_bins (np.array): extracted velocity bins of the signal (same length as signal)

    Returns:
        array containing:

            - reflectivity (0th moment) over range of velocity bins [mm6/m3]
            - mean velocity (1st moment) over range of velocity bins [m/s]
            - spectrum width (2nd moment) over range of velocity bins [m/s]
            - skewness (3rd moment) over range of velocity bins
            - kurtosis (4th moment) over range of velocity bins

    """

    signal_sum = np.sum(signal)  # linear full spectrum Ze [mm^6/m^3], scalar
    ze_lin = signal_sum / 2.0
    pwr_nrm = signal / signal_sum  # determine normalized power (NOT normalized by Vdop bins)
    vel = np.sum(vel_bins * pwr_nrm)
    vel_diff = vel_bins - vel
    vel_diff2 = vel_diff * vel_diff
    sw = np.sqrt(np.abs(np.sum(pwr_nrm * vel_diff2)))
    sw2 = sw * sw
    skew = np.sum(pwr_nrm * vel_diff * vel_diff2 / (sw * sw2))
    kurt = np.sum(pwr_nrm * vel_diff2 * vel_diff2 / (sw2 * sw2))
    return np.array((ze_lin, vel, sw, skew, kurt), dtype=np.float32)


@jit(nopython=True, fastmath=True)
def find_peak_edges(signal: np.array) -> Tuple[int, int]:
    """Returns the indices of left and right edge of the main signal peak in a Doppler spectra.

    Args:
        signal (np.array): 1D array Doppler spectra

    Returns:
        tuple: 2-element tuple containing the left / right indices of the main peak edges

    """
    len_sig = len(signal)
    edge_left, edge_right = 0, len_sig
    threshold = np.min(signal)
    imax = np.argmax(signal)

    for ind in range(imax, len_sig):
        if signal[ind] > threshold:
            continue
        edge_right = ind
        break

    for ind in range(imax, -1, -1):
        if signal[ind] > threshold:
            continue
        edge_left = ind + 1  # the +1 is important, otherwise a fill_value will corrupt the numba code
        break

    return edge_left, edge_right


def spectral_LDR_Galetti(TotSpec: np.array, HSpec: np.array, ReVHSpec:np.array, ImVHSpec: np.array,
                         TotNoisePow: np.array, HNoisePow: np.array, SpecN: np.array, RAltN: int, RngOffs: np.array,
                         version: int
                         ) -> np.array:
    """
    Compute spectral (S)LDR for vertically pointing radar according to the method by Galetti et al. (2012)
    Based on code by Alexander Myagkov (RPG).
    For RPG radars software version > 5.40, the combined spectrum is normalized by 4 (previously 2)
    Args:
        TotSpec: V+H power spectra
        HSpec: only horizontal channel power spectra
        ReVHSpec: covariance spectrum Re
        ImVHSpec: covariance spectrum imaginary part
        TotNoisePow: noise power V+H
        HNoisePow: noise power only H channel
        SpecN: number of FFT points
        RAltN: number of range layers
        RngOffs: range offsets
        version: software version of RPG radar

    Returns:
        np.array: SLDR computed accordring to the Galetti method

    """
    if version < 5.40:
        VSpec = 2 * TotSpec - HSpec - 2 * ReVHSpec
    else:
        VSpec = 4 * TotSpec - HSpec - 2 * ReVHSpec
    bins_per_chirp = np.diff(np.hstack((RngOffs, RAltN)))
    noise_h_per_bin = (HNoisePow/np.repeat(SpecN, bins_per_chirp))[:, :, np.newaxis]
    noise_v_per_bin = (TotNoisePow/np.repeat(SpecN, bins_per_chirp))[:, :, np.newaxis]
    SNRv = VSpec/noise_v_per_bin
    SNRh = HSpec/noise_h_per_bin
    k = ((SNRv < 1000) | (SNRh < 1000))

    rhv = np.abs(ReVHSpec+complex(imag=1) * ImVHSpec) / np.sqrt(
        (VSpec + noise_v_per_bin) * (HSpec + noise_h_per_bin))
    sldr = 10*np.log10((1-rhv)/(1+rhv))
    k = (k | (TotSpec == 0.))
    sldr[k] = -999
    return sldr