import datetime
import os
from pathlib import Path
from typing import Dict, NamedTuple, Tuple, Union

import numpy as np
import pytz
from numpy import ma


def get_current_time() -> str:
    """Returns current UTC time."""
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def rpg_seconds2date(time_stamp: float, date_only: bool = False) -> list:
    """Convert RPG timestamp to UTC date + time.

    Args:
        time_stamp (int): RPG timestamp.
        date_only (bool): If true, return only date (no time).

    Returns:
        list: UTC date + optionally time in format ['YYYY', 'MM', 'DD', 'hh', 'min', 'sec']

    """
    epoch = (2001, 1, 1)
    epoch_in_seconds = datetime.datetime.timestamp(datetime.datetime(*epoch, tzinfo=pytz.utc))
    time_stamp += epoch_in_seconds
    date_time = datetime.datetime.utcfromtimestamp(time_stamp).strftime("%Y %m %d %H %M %S").split()
    if date_only:
        return date_time[:3]
    return date_time


def rpg_seconds2datetime64(timestamps: np.ndarray) -> np.ndarray:
    """Convert NumPy array of RPG timestamps to datetime64 in UTC."""
    return np.datetime64("2001-01-01") + timestamps.astype("timedelta64[s]")


class RpgStatusFlags(NamedTuple):
    """
    Status flag is a float which (as of 2022-11-17) can have up to 4 digits
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
    valid_ind = tmp == flags
    output = {}
    for key in ["heater", "blower", "hatpro_temperature", "hatpro_humidity"]:
        tmp, values = np.divmod(tmp, 10)
        valid_ind &= values <= 1
        output[key] = values
    masked_output: Dict[str, ma.MaskedArray] = {
        key: ma.masked_array(values, mask=valid_ind) for key, values in output.items()
    }
    return RpgStatusFlags(**masked_output)


def get_rpg_file_type(header: dict) -> Tuple[int, int]:
    """Find level and version of RPG cloud radar binary file.

    Args:
        header (dict): Header of the radar file containing *file_code* key.

    Returns:
        tuple: 2-element tuple containing Level (0 or 1) and Version (2, 3 or 4).

    Raises:
        RuntimeError: Unknown file type.

    """
    file_code = header["FileCode"]
    if file_code == 789346:
        return 0, 2
    if file_code == 889346:
        return 0, 3
    if file_code == 789347:
        return 1, 2
    if file_code == 889347:
        return 1, 3
    if file_code == 889348:
        return 1, 4
    raise RuntimeError("Unknown RPG binary file.")


def isscalar(array) -> bool:
    """Tests if input is scalar.

    By "scalar" we mean that array has a single value.

    Examples:
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


def create_velocity_vectors(header: dict) -> ma.masked_array:
    """Create Doppler velocity vector for each chirp.

    Args:
        header (dict): Header of the radar file.

    Returns:
       maskedArray: Doppler velocity vector for each chirp. These are equally long
           vectors (max number of bins) where the padded values are masked.

    """
    n_chirps = header["SequN"]
    n_bins_max = np.max(header["SpecN"])
    velocity_vectors = ma.masked_all((n_chirps, n_bins_max))
    for ind, (n_bins, chirp_max_vel) in enumerate(zip(header["SpecN"], header["MaxVel"])):
        bins_to_shift = (n_bins_max - n_bins) // 2
        dopp_res = chirp_max_vel / n_bins
        velocity = np.linspace(-chirp_max_vel + dopp_res, +chirp_max_vel - dopp_res, n_bins)
        velocity_vectors[ind, bins_to_shift : bins_to_shift + len(velocity)] = velocity
    return velocity_vectors


def str2path(path: Union[Path, str, None]) -> Path:
    """Converts path as str to pathlib.Path."""
    if path is None:
        return Path(os.getcwd())
    return Path(path) if isinstance(path, str) else path
