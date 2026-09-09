import os

import pytest

from rpgpy import RPGFileError, read_rpg

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


def test_invalid_file():
    input_file = f"{FILE_PATH}/../data/corrupted_files/230401_000001_P00_ZEN.LV1"
    with pytest.raises(RPGFileError):
        read_rpg(input_file)


def test_long_names_level0_stsr():
    filename = f"{FILE_PATH}/../data/level0/v3-889346/190912_060003_P05_ZEN.LV0"
    header, data = read_rpg(filename, rpg_names=False)
    assert header["Dual Polarisation"] == 2
    assert "Linear Depolarisation Ratio" not in data
    assert "Differential Reflectivity Ratio" not in data
    assert "Doppler Spectrum" in data


def test_long_names_level1_stsr():
    filename = f"{FILE_PATH}/../data/level1/v3-889347/190801_070001_P05_ZEN.LV1"
    header, data = read_rpg(filename, rpg_names=False)
    assert header["Dual Polarisation"] == 2
    assert "Linear Depolarisation Ratio" not in data
    assert "Differential Reflectivity Ratio" in data
