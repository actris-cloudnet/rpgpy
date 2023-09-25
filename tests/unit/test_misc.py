import os

import pytest

from rpgpy import RPGFileError, read_rpg

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


def test_invalid_file():
    input_file = f"{FILE_PATH}/../data/corrupted_files/230401_000001_P00_ZEN.LV1"
    with pytest.raises(RPGFileError):
        read_rpg(input_file)
