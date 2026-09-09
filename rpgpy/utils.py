from __future__ import annotations

import datetime
import importlib
from typing import TYPE_CHECKING, NamedTuple

import numpy as np
from numpy import ma

if TYPE_CHECKING:
    from collections.abc import Callable


def _find_madvise_hugepage_setter() -> Callable[[bool], bool] | None:
    for module_name in ("numpy._core.multiarray", "numpy.core.multiarray"):
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            continue
        setter = getattr(module, "_set_madvise_hugepage", None)
        if setter is not None:
            return setter
    return None


_set_madvise_hugepage = _find_madvise_hugepage_setter()


class RPGFileError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, msg: str = "Problem with reading file"):
        self.message = msg
        super().__init__(self.message)


def zeros_no_hugepage(shape: tuple[int, ...], dtype: type | str) -> np.ndarray:
    """Allocates a zero-filled array without transparent huge pages.

    NumPy asks the kernel for huge pages on large allocations. Sparse writes into
    such an array (e.g. compressed spectra) then trigger a slow huge page allocation
    attempt on every first-touched 4 kB page, making the read tens of times slower
    on Linux. Untouched pages of the returned array stay unmapped, so memory usage
    follows the amount of actual data instead of the array size.
    """
    if _set_madvise_hugepage is None:
        return np.zeros(shape, dtype)
    previous = _set_madvise_hugepage(False)  # noqa: FBT003
    try:
        return np.zeros(shape, dtype)
    finally:
        _set_madvise_hugepage(previous)


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
    if file_code in (889346, 1889346):
        return 0, 3.5
    if file_code == 789345:
        return 1, 1.0
    if file_code == 789347:
        return 1, 2.0
    if file_code in (889347, 1889347):
        return 1, 3.5
    if file_code in (889348, 1889348):
        return 1, 4.0
    msg = f"Unknown file type. File code: {file_code}"
    raise RPGFileError(msg)


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
