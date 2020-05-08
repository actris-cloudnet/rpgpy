import numpy.ma as ma
import datetime


def get_current_time():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def rpg_seconds2date(time_stamp):
    epoch = datetime.datetime(2001, 1, 1).timestamp()
    time_stamp += epoch
    return datetime.datetime.utcfromtimestamp(time_stamp).strftime('%Y %m %d').split()


def get_rpg_file_type(header):
    """Find level and version of RPG cloud radar binary file.

    Args:
        header (dict): Header of the radar file containing *file_code* key.

    Returns:
        tuple: 2-element tuple containing Level (0 or 1) and Version (2 or 3).

    Raises:
        RuntimeError: Unknown file type.

    """
    file_code = header['FileCode']
    if file_code == 789346:
        return 0, 2
    elif file_code == 889346:
        return 0, 3
    elif file_code == 789347:
        return 1, 2
    elif file_code == 889347:
        return 1, 3
    raise RuntimeError('Unknown RPG binary file.')


def isscalar(array):
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
    if not hasattr(arr, '__len__') or arr.shape == () or len(arr) == 1:
        return True
    return False
