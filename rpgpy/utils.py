from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import NamedTuple

import numpy as np
from numpy import ma


def get_current_time() -> str:
    """Returns current UTC time."""
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def rpg_seconds2datetime64(
    seconds: np.ndarray,
    milliseconds: np.ndarray | None = None,
) -> np.ndarray:
    """Convert RPG timestamps to datetime64 in UTC.

    Args:
    ----
        seconds (np.ndarray): A NumPy array of seconds since 2001-01-01.
        milliseconds (np.ndarray, optional): A NumPy array of milliseconds.

    Returns:
    -------
        np.ndarray: A NumPy array of datetime64 timestamps in UTC.

    """
    if milliseconds is None:
        milliseconds = np.zeros_like(seconds)
    return (
        np.datetime64("2001-01-01")
        + seconds.astype("timedelta64[s]")
        + milliseconds.astype("timedelta64[ms]")
    )


class RpgStatusFlags(NamedTuple):
    """Status flag is a float which (as of 2022-11-17) can have up to 4 digits
    (WXYZ), where:
    - Z (least significant digit) is 1 when heater is on, otherwise 0 (please
        note, that no RPG radar has a physical heater)
    - Y is 1 when blower is on, otherwise 0
    - X is 1 when temperature profile is from a coupled HATPRO, otherwise 0
    - W is 1 when humidity profiles are from a coupled HATPRO, otherwise 0
    """

    heater: ma.MaskedArray
    blower: ma.MaskedArray
    hatpro_temperature: ma.MaskedArray
    hatpro_humidity: ma.MaskedArray


def decode_rpg_status_flags(flags: np.ndarray) -> RpgStatusFlags:
    tmp = flags.astype(np.uint32)
    mask = tmp != flags
    output = {}
    for key in ["heater", "blower", "hatpro_temperature", "hatpro_humidity"]:
        tmp, values = np.divmod(tmp, 10)
        mask |= values > 1
        output[key] = values
    masked_output: dict[str, ma.MaskedArray] = {
        key: ma.masked_array(values, mask) for key, values in output.items()
    }
    return RpgStatusFlags(**masked_output)


def get_rpg_file_type(header: dict) -> tuple[int, float]:
    """Find level and version of RPG cloud radar binary file.

    Args:
    ----
        header (dict): Header of the radar file containing *file_code* key.

    Returns:
    -------
        tuple: 2-element tuple containing Level (0 or 1) and Version (1.0, 2.0, 3.5
            or 4.0).

    Raises:
    ------
        RuntimeError: Unknown file type.

    """
    file_code = header["FileCode"]
    if file_code == 789346:
        return 0, 2.0
    if file_code == 889346:
        return 0, 3.5
    if file_code == 789345:
        return 1, 1.0
    if file_code == 789347:
        return 1, 2.0
    if file_code == 889347:
        return 1, 3.5
    if file_code == 889348:
        return 1, 4.0
    msg = f"Unknown file type. File code: {file_code}"
    raise RuntimeError(msg)


def isscalar(array) -> bool:
    """Tests if input is scalar.

    By "scalar" we mean that array has a single value.

    Examples
    --------
        >>> isscalar(1)
            True
        >>> isscalar([1])
            True
        >>> isscalar(np.array(1))
            True
        >>> isscalar(np.array([1]))
            True

    """
    arr = ma.array(array)
    if not hasattr(arr, "__len__") or arr.shape == () or len(arr) == 1:
        return True
    return False


def create_velocity_vectors(header: dict) -> np.ndarray:
    """Create Doppler velocity vector for each chirp.

    Args:
    ----
        header (dict): Header of the radar file.

    Returns:
    -------
       np.ndarray: Doppler velocity vector for each chirp. These are equally long
           vectors (max number of bins) where the padded values are masked.

    """
    n_chirps = header["SequN"]
    n_bins_max = np.max(header["SpecN"])
    # zeros will be automatically masked in the netCDF file:
    velocity_vectors = np.zeros((n_chirps, n_bins_max))
    for ind, (n_bins, chirp_max_vel) in enumerate(
        zip(header["SpecN"], header["MaxVel"], strict=True),
    ):
        bins_to_shift = (n_bins_max - n_bins) // 2
        dopp_res = chirp_max_vel / n_bins
        velocity = np.linspace(
            -chirp_max_vel + dopp_res,
            +chirp_max_vel - dopp_res,
            n_bins,
        )
        velocity_vectors[ind, bins_to_shift : bins_to_shift + len(velocity)] = velocity
    return velocity_vectors


def str2path(path: Path | str | None) -> Path:
    """Converts path as str to pathlib.Path."""
    if path is None:
        return Path(os.getcwd())
    return Path(path) if isinstance(path, str) else path
