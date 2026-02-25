from __future__ import annotations

import logging
from typing import Literal

import numpy as np

_first_call = True

try:
    from numba import jit

    JIT = jit(nopython=True, fastmath=True)
except ImportError:

    def JIT(func):
        def wrapper(*args, **kwargs):
            global _first_call  # noqa: PLW0603
            if _first_call:
                logging.warning(
                    "Numba not installed — running without JIT acceleration."
                )
                _first_call = False
            return func(*args, **kwargs)

        return wrapper


def spectra2moments(
    data: dict,
    header: dict,
    spec_var: Literal["TotSpec", "VSpec", "HSpec"] | None = None,
    *,
    fill_value: float = -999.0,
    n_points_min: int = 4,
    largest_peak: bool = True,
) -> dict:
    """Calculates radar moments.

    This routine calculates the radar moments: reflectivity, mean Doppler velocity,
    spectrum width, skewness and kurtosis from compressed level 0 spectrum files
    (NoiseFactor > 0) of the 94 GHz RPG cloud radar.

    Args:
    ----
        data: Level 0 nD variables.
        header: Level 0 metadata.
        spec_var: Name of the spectral variable. Possible names are 'TotSpec', 'VSpec',
            and 'HSpec'. Defaults to 'TotSpec' in STSR mode and 'VSpec' otherwise.
        fill_value: Clear sky fill value.
        n_points_min: Minimum number of points in a valid spectral line.
        largest_peak: If True, consider only the largest peak. Otherwise, use
            the whole spectra. Defaults to True.

    Returns:
    -------
        A dict with keys: 'Ze', 'MeanVel', 'SpecWidth', 'Skewn', 'Kurt'.

    Examples:
    --------
        >>> from rpgpy import read_rpg, spectra2moments
        >>> header, data = read_rpg('rpg-fmcw-94-file.LV0')
        >>> moments = spectra2moments(data, header)

    """
    if spec_var is None:
        spec_var = "TotSpec" if header["DualPol"] == 2 else "VSpec"
    spectra = data[spec_var]
    n_time, n_range, max_n_spec = spectra.shape
    moments = np.full((n_time, n_range, 5), np.nan)
    no_signal = np.all(spectra == 0, axis=2)
    ranges = np.append(header["RngOffs"], header["RAltN"])
    velocity_vector = header["velocity_vectors"]

    for ind_chirp in range(header["SequN"]):
        n_spec = header["SpecN"][ind_chirp]
        spec_left = (max_n_spec - n_spec) // 2
        spec_right = spec_left + n_spec
        for ind_range in range(ranges[ind_chirp], ranges[ind_chirp + 1]):
            for ind_time in range(n_time):
                if no_signal[ind_time, ind_range]:
                    continue
                edge_left, edge_right = find_peak_edges(spectra[ind_time, ind_range, :])
                if (edge_right - edge_left) < n_points_min:
                    no_signal[ind_time, ind_range] = True
                    continue
                if not largest_peak:
                    edge_left, edge_right = spec_left, spec_right
                moments[ind_time, ind_range, :] = radar_moment_calculation(
                    spectra[ind_time, ind_range, edge_left:edge_right],
                    velocity_vector[ind_chirp, edge_left:edge_right],
                )

    output = {
        key: moments[:, :, i]
        for i, key in enumerate(["Ze", "MeanVel", "SpecWidth", "Skewn", "Kurt"])
    }
    for key in output:
        output[key][no_signal] = fill_value
    return output


@JIT
def radar_moment_calculation(signal: np.ndarray, vel_bins: np.ndarray) -> np.ndarray:
    """Calculates radar moments from one a single spectral line.

    Calculation reflectivity, mean Doppler velocity, spectral width,
    skewness, and kurtosis of one Doppler spectrum. Optimized for the use of Numba.

    Args:
    ----
        signal: Detected signal from a Doppler spectrum.
        vel_bins: Extracted velocity bins of the signal (same length as signal).

    Returns:
    -------
        array containing:

            - Reflectivity (0th moment) over range of velocity bins [mm6/m3]
            - Mean velocity (1st moment) over range of velocity bins [m/s]
            - Spectrum width (2nd moment) over range of velocity bins [m/s]
            - Skewness (3rd moment) over range of velocity bins
            - Kurtosis (4th moment) over range of velocity bins

    """
    signal_sum = np.sum(signal)  # linear full spectrum Ze [mm^6/m^3], scalar
    ze_lin = (
        signal_sum / 2.0
    )  # divide by 2 because vertical and horizontal channel are added.
    pwr_nrm = (
        signal / signal_sum
    )  # determine normalized power (NOT normalized by Vdop bins)
    vel = np.sum(vel_bins * pwr_nrm)
    vel_diff = vel_bins - vel
    vel_diff2 = vel_diff * vel_diff
    sw2 = np.sum(pwr_nrm * vel_diff2)
    sw = np.sqrt(sw2)
    skew = np.sum(pwr_nrm * vel_diff * vel_diff2 / (sw * sw2))
    kurt = np.sum(pwr_nrm * vel_diff2 * vel_diff2 / (sw2 * sw2))
    return np.array((ze_lin, vel, sw, skew, kurt), dtype=np.float32)


@jit(nopython=True, fastmath=True)
def _screen_noise(spectra, ranges, sequ_n, spec_n):
    n_time, n_range, max_n_spec = spectra.shape
    for ind_time in range(n_time):
        for ind_chirp in range(sequ_n):
            n_spec = spec_n[ind_chirp]
            for ind_range in range(ranges[ind_chirp], ranges[ind_chirp + 1]):
                ind_left = (max_n_spec - n_spec) // 2
                ind_right = ind_left + n_spec
                signal = spectra[ind_time, ind_range, ind_left:ind_right]
                ssignal = np.sort(signal)
                Sum = 0
                SumSq = 0
                for i in range(n_spec):
                    N = i + 1
                    LastSum = Sum
                    LastSumSq = SumSq
                    Sum += ssignal[i]
                    SumSq += ssignal[i] ** 2
                    if 2 * Sum**2 < N * SumSq:
                        Sum = LastSum
                        SumSq = LastSumSq
                        N -= 1
                        break
                Mean = Sum / N
                Var = SumSq / N - Mean**2
                Std = np.sqrt(Var)
                threshold = Mean + 6 * Std
                signal[signal < threshold] = 0


def screen_noise(data: dict, header: dict):
    """Screen noise from Doppler spectra using Hildebrand and Sehkon (1974).

    Note that given data is modified inplace.

    Args:
    ----
        data: Level 0 nD variables.
        header: Level 0 metadata.

    References:
    ----------

    Hildebrand, P. H., & Sekhon, R. S. (1974). Objective determination of the
    noise level in Doppler spectra. Journal of Applied Meteorology and
    Climatology, 13(7), 808-811.
    """
    spec_var = "TotSpec" if header["DualPol"] == 2 else "VSpec"
    spectra = data[spec_var]
    ranges = np.append(header["RngOffs"], header["RAltN"])
    sequ_n = header["SequN"]
    spec_n = header["SpecN"]
    _screen_noise(spectra, ranges, sequ_n, spec_n)


@JIT
def find_peak_edges(signal: np.ndarray) -> tuple[int, int]:
    """Returns the indices of left and right edge of the main signal peak in a Doppler
    spectra.

    Args:
    ----
        signal: 1D array Doppler spectra.

    Returns:
    -------
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
    ----
        header: Level 0 nD variables.
        data: Level 0 nD metadata.

    Returns:
    -------
        Computed SLDR [dB].

    """
    spec_tot = scale_spectra(data["TotSpec"], header["SWVersion"])
    spec_V = spec_tot - data["HSpec"] - 2 * data["ReVHSpec"]
    noise_V = (
        data["TotNoisePow"] / 2.0
    )  # TBD: how to obtain noise power in vertical channel?

    bins_per_chirp = np.diff(np.hstack((header["RngOffs"], header["RAltN"])))
    noise_h_per_bin = (data["HNoisePow"] / np.repeat(header["SpecN"], bins_per_chirp))[
        :,
        :,
        np.newaxis,
    ]
    noise_v_per_bin = (noise_V / np.repeat(header["SpecN"], bins_per_chirp))[
        :,
        :,
        np.newaxis,
    ]

    # Avoid division by zero
    noise_v_per_bin[noise_v_per_bin == 0] = 1e-10
    noise_h_per_bin[noise_h_per_bin == 0] = 1e-10

    SNRv = spec_V / noise_v_per_bin
    SNRh = data["HSpec"] / noise_h_per_bin
    snr_mask = (SNRv < 1000) | (SNRh < 1000)
    rhv = np.abs(data["ReVHSpec"] + complex(imag=1) * data["ImVHSpec"]) / np.sqrt(
        (spec_V + noise_v_per_bin) * (data["HSpec"] + noise_h_per_bin),
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
    ----
        signal: Combined spectrum (TotSpec).
        software_version: 10 * radar software version number.

    Returns:
    -------
        Scaled spectra.

    """
    scale = 2 if software_version < 540 else 4
    return scale * signal
