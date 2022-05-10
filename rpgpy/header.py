"""Module for reading RPG 94 GHz radar header."""
from pathlib import Path
from typing import Iterator, Tuple

import numpy as np

from rpgpy import utils


def read_rpg_header(file_name: Path) -> Tuple[dict, int]:
    """Reads header from RPG binary file.

    Supports Level 0/1 and version 2/3/4.

    Args:
        file_name: name of the file.

    Returns:
        2-element tuple containing the header (as dict) and file position.

    """

    def read(*fields):
        block = np.fromfile(file, np.dtype(list(fields)), 1)
        for name in block.dtype.names:
            array = block[name][0]
            if utils.isscalar(array):
                header[name] = array
            else:
                header[name] = np.array(array, dtype=_get_dtype(array))

    header: dict = {}
    file = open(file_name, "rb")  # pylint: disable=R1732

    read(("FileCode", "i4"), ("HeaderLen", "i4"))

    level, version = utils.get_rpg_file_type(header)

    if version > 2:
        read(("StartTime", "uint32"), ("StopTime", "uint32"))

    read(("CGProg", "i4"), ("ModelNo", "i4"))

    header["ProgName"] = _read_string(file)
    header["CustName"] = _read_string(file)

    read(("Freq", "f"), ("AntSep", "f"), ("AntDia", "f"), ("AntG", "f"), ("HPBW", "f"))

    if level == 0:
        read(("Cr", "f"))

    read(("DualPol", "i1"))

    if level == 0:
        read(("CompEna", "i1"), ("AntiAlias", "i1"))

    read(
        ("SampDur", "f"),
        ("GPSLat", "f"),
        ("GPSLong", "f"),
        ("CalInt", "i4"),
        ("RAltN", "i4"),
        ("TAltN", "i4"),
        ("HAltN", "i4"),
        ("SequN", "i4"),
    )

    n_levels, n_temp, n_humidity, n_chirp = _get_number_of_levels(header)

    read(("RAlts", _dim(n_levels)), ("TAlts", _dim(n_temp)), ("HAlts", _dim(n_humidity)))

    if level == 0:
        read(("Fr", _dim(n_levels)))

    read(
        ("SpecN", _dim(n_chirp, "i4")),
        ("RngOffs", _dim(n_chirp, "i4")),
        ("ChirpReps", _dim(n_chirp, "i4")),
        ("SeqIntTime", _dim(n_chirp)),
        ("dR", _dim(n_chirp)),
        ("MaxVel", _dim(n_chirp)),
    )

    if version > 2:
        if level == 0:
            read(
                ("ChanBW", _dim(n_chirp)),
                ("ChirpLowIF", _dim(n_chirp, "i4")),
                ("ChirpHighIF", _dim(n_chirp, "i4")),
                ("RangeMin", _dim(n_chirp, "i4")),
                ("RangeMax", _dim(n_chirp, "i4")),
                ("ChirpFFTSize", _dim(n_chirp, "i4")),
                ("ChirpInvSamples", _dim(n_chirp, "i4")),
                ("ChirpCenterFr", _dim(n_chirp)),
                ("ChirpBWFr", _dim(n_chirp)),
                ("FFTStartInd", _dim(n_chirp, "i4")),
                ("FFTStopInd", _dim(n_chirp, "i4")),
                ("ChirpFFTNo", _dim(n_chirp, "i4")),
                ("SampRate", "i4"),
                ("MaxRange", "i4"),
            )

        read(
            ("SupPowLev", "i1"),
            ("SpkFilEna", "i1"),
            ("PhaseCorr", "i1"),
            ("RelPowCorr", "i1"),
            ("FFTWindow", "i1"),
            ("FFTInputRng", "uint16"),
            ("SWVersion", "uint16"),
            ("NoiseFilt", "f4"),
        )

        if level == 1 and version > 3.5:
            read(("InstCalPar", "i4"))
        elif level == 0:
            _ = np.fromfile(file, "i4")

        if level == 0 or (level == 1 and version > 3.5):
            _ = np.fromfile(file, "i4", 24)
            _ = np.fromfile(file, "uint32", 10000)

    if level == 0:
        header["velocity_vectors"] = utils.create_velocity_vectors(header)

    file_position = file.tell()
    file.close()

    return header, file_position


def _read_string(file_id) -> str:
    """Read characters from binary data until whitespace."""
    str_out = ""
    while True:
        value = np.fromfile(file_id, np.int8, 1)
        if value:
            try:
                str_out += chr(value[0])
            except ValueError:
                str_out += "%"
        else:
            break
    return str_out


def _get_number_of_levels(header: dict) -> Iterator[int]:
    for name in ("RAltN", "TAltN", "HAltN", "SequN"):
        yield int(header[name])


def _dim(length: int, dtype: str = "f") -> str:
    return f"({length},){dtype}"


def _get_dtype(array: np.ndarray) -> type:
    if array.dtype in (np.int8, np.int32, np.uint32):
        return int
    return float
