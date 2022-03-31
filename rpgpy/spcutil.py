from typing import Optional, Tuple

import numpy as np
from numba import jit


def spectra2moments(
    data: dict,
    header: dict,
    spec_var: Optional[str] = "TotSpec",
    fill_value: Optional[float] = -999.0,
    n_points_min: Optional[int] = 4,
) -> dict:
    """Calculates radar moments from the main peak.

    This routine calculates the radar moments: reflectivity, mean Doppler velocity, spectrum
    width, skewness and kurtosis from compressed level 0 spectrum files (NoiseFactor > 0)
    of the 94 GHz RPG cloud radar. Considering only the largest peak.

    Args:
        data: Level 0 nD variables.
        header: Level 0 meta data.
        spec_var: Name of the spectral variable. Possible names are 'TotSpec', 'VSpec', and 'HSpec'.
        fill_value: Clear sky fill value.
        n_points_min: Minimum number of points in a valid spectral line.

    Returns:
        A dict with keys: 'Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'.

    Examples:
        >>> from rpgpy import read_rpg, spectra2moments
        >>> header, data = read_rpg('rpg-fmcw-94-file.LV0')
        >>> moments = spectra2moments(data, header)

    """
    spectra = data[spec_var]
    n_time, n_range, _ = spectra.shape
    moments = np.full((n_time, n_range, 5), np.nan)
    no_signal = np.all(spectra == 0, axis=2)
    ranges = np.append(header["RngOffs"], header["RAltN"])

    for ind_chirp in range(header["SequN"]):
        dopp_res = np.mean(np.diff(header["velocity_vectors"][ind_chirp]))
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
                    header["velocity_vectors"][ind_chirp][edge_left:edge_right],
                )

        # shift mean Doppler velocity by half a bin
        moments[:, ranges[ind_chirp] : ranges[ind_chirp + 1], 1] -= dopp_res / 2.0

    output = {
        key: moments[:, :, i]
        for i, key in enumerate(["Ze", "MeanVel", "SpecWidth", "Skewn", "Kurt"])
    }
    for key in output.keys():
        output[key][no_signal] = fill_value
    return output


@jit(nopython=True, fastmath=True)
def radar_moment_calculation(signal: np.ndarray, vel_bins: np.ndarray) -> np.ndarray:
    """Calculates radar moments from one a single spectral line.

    Calculation reflectivity, mean Doppler velocity, spectral width,
    skewness, and kurtosis of one Doppler spectrum. Optimized for the use of Numba.

    Args:
        signal: Detected signal from a Doppler spectrum.
        vel_bins: Extracted velocity bins of the signal (same length as signal).

    Returns:
        array containing:

            - Reflectivity (0th moment) over range of velocity bins [mm6/m3]
            - Mean velocity (1st moment) over range of velocity bins [m/s]
            - Spectrum width (2nd moment) over range of velocity bins [m/s]
            - Skewness (3rd moment) over range of velocity bins
            - Kurtosis (4th moment) over range of velocity bins

    """

    signal_sum = np.sum(signal)  # linear full spectrum Ze [mm^6/m^3], scalar
    ze_lin = signal_sum / 2.0  # divide by 2 because vertical and horizontal channel are added.
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
def find_peak_edges(signal: np.ndarray) -> Tuple[int, int]:
    """Returns the indices of left and right edge of the main signal peak in a Doppler spectra.

    Args:
        signal: 1D array Doppler spectra.

    Returns:
        2-element tuple containing the left / right indices of the main peak edges.

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
        edge_left = (
            ind + 1
        )  # the +1 is important, otherwise a fill_value will corrupt the numba code
        break

    return edge_left, edge_right


def calc_spectral_LDR(header: dict, data: dict) -> np.ndarray:
    """Computes spectral (S)LDR for vertically pointing STSR radar.

    Method by Galetti et al. (2012); Based on code by Alexander Myagkov (RPG).

    Args:
        header: Level 0 nD variables.
        data: Level 0 nD metadata.

    Returns:
        Computed SLDR [dB].

    """
    spec_tot = scale_spectra(data["TotSpec"], header["SWVersion"])
    spec_V = spec_tot - data["HSpec"] - 2 * data["ReVHSpec"]
    noise_V = data["TotNoisePow"] / 2.0  # TBD: how to obtain noise power in vertical channel?

    bins_per_chirp = np.diff(np.hstack((header["RngOffs"], header["RAltN"])))
    noise_h_per_bin = (data["HNoisePow"] / np.repeat(header["SpecN"], bins_per_chirp))[
        :, :, np.newaxis
    ]
    noise_v_per_bin = (noise_V / np.repeat(header["SpecN"], bins_per_chirp))[:, :, np.newaxis]
    SNRv = spec_V / noise_v_per_bin
    SNRh = data["HSpec"] / noise_h_per_bin
    snr_mask = (SNRv < 1000) | (SNRh < 1000)

    rhv = np.abs(data["ReVHSpec"] + complex(imag=1) * data["ImVHSpec"]) / np.sqrt(
        (spec_V + noise_v_per_bin) * (data["HSpec"] + noise_h_per_bin)
    )
    sldr = 10 * np.log10((1 - rhv) / (1 + rhv))
    snr_mask = snr_mask | (data["TotSpec"] == 0.0)
    sldr[snr_mask] = -999
    return sldr


def scale_spectra(signal: np.ndarray, software_version: float) -> np.ndarray:
    """Scales combined spectrum.

    Starting from software version 5.40, the combined spectrum is normalized by 4.
    For previous versions, the combined spectrum was normalized by 2.
    Only for STSR mode radar (TBD).

    Args:
        signal: Combined spectrum (TotSpec).
        software_version: 10 * radar software version number.

    Returns:
        Scaled spectra.

    """
    scale = 2 if software_version < 540 else 4
    return scale * signal
