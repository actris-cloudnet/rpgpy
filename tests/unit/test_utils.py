import numpy as np
import pytest
from numpy.testing import assert_array_equal

from rpgpy import spcutil, utils


def test_rpg_seconds2date():
    date = utils.rpg_seconds2date(0)
    date_only = utils.rpg_seconds2date(0, date_only=True)
    res = ["2001", "01", "01", "00", "00", "00"]
    assert_array_equal(date, res)
    assert_array_equal(date_only, res[:3])


@pytest.mark.parametrize(
    "data, result",
    [
        (0, ["2001", "01", "01", "00", "00", "00"]),
        (24 * 60 * 60 * 10 + 1, ["2001", "01", "11", "00", "00", "01"]),
        (24 * 60 * 60 - 1, ["2001", "01", "01", "23", "59", "59"]),
        (625107602, ["2020", "10", "23", "01", "00", "02"]),
    ],
)
def test_seconds2date(data, result):
    assert utils.rpg_seconds2date(data) == result


def test_seconds2datetime64():
    assert_array_equal(
        utils.rpg_seconds2datetime64(
            np.array([0, 24 * 60 * 60 * 10 + 1, 24 * 60 * 60 - 1, 625107602])
        ),
        np.array(
            [
                "2001-01-01T00:00:00",
                "2001-01-11T00:00:01",
                "2001-01-01T23:59:59",
                "2020-10-23T01:00:02",
            ],
            dtype="datetime64",
        ),
    )


def test_with_valid_status_flags():
    flags = utils.decode_rpg_status_flags(np.array([0.0, 1.0, 10.0, 1100.0, 1010101.0]))
    assert_array_equal(flags.heater.data, [0, 1, 0, 0, 1])
    assert_array_equal(flags.blower.data, [0, 0, 1, 0, 0])
    assert_array_equal(flags.hatpro_temperature.data, [0, 0, 0, 1, 1])
    assert_array_equal(flags.hatpro_humidity.data, [0, 0, 0, 1, 0])
    assert_array_equal(flags.heater.mask, [0, 0, 0, 0, 0])
    assert_array_equal(flags.blower.mask, [0, 0, 0, 0, 0])
    assert_array_equal(flags.hatpro_temperature.mask, [0, 0, 0, 0, 0])
    assert_array_equal(flags.hatpro_humidity.mask, [0, 0, 0, 0, 0])


def test_with_invalid_status_flags():
    flags = utils.decode_rpg_status_flags(np.array([10.0, 1.1, 9.0, 211.0]))
    assert flags.heater.data[0] == 0
    assert flags.blower.data[0] == 1
    assert flags.hatpro_temperature.data[0] == 0
    assert flags.hatpro_humidity.data[0] == 0
    assert_array_equal(flags.heater.mask, [0, 1, 1, 1])
    assert_array_equal(flags.blower.mask, [0, 1, 1, 1])
    assert_array_equal(flags.hatpro_temperature.mask, [0, 1, 1, 1])
    assert_array_equal(flags.hatpro_humidity.mask, [0, 1, 1, 1])


def test_create_velocity_vectors():
    inp = {"SpecN": [20], "MaxVel": [10], "SequN": 1}
    res = [
        [
            -9.5,
            -8.5,
            -7.5,
            -6.5,
            -5.5,
            -4.5,
            -3.5,
            -2.5,
            -1.5,
            -0.5,
            0.5,
            1.5,
            2.5,
            3.5,
            4.5,
            5.5,
            6.5,
            7.5,
            8.5,
            9.5,
        ]
    ]
    assert_array_equal(utils.create_velocity_vectors(inp), res)

    inp = {"SpecN": [4, 10], "MaxVel": [8, 5], "SequN": 2}
    res = [
        [0, 0, 0, -6, -2, 2, 6, 0, 0, 0],
        [-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
    ]
    mask = [[1, 1, 1, 0, 0, 0, 0, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    assert_array_equal(utils.create_velocity_vectors(inp), res)
    assert_array_equal(utils.create_velocity_vectors(inp).mask, mask)


def test_find_peak_edges():
    inp = np.array([0, 0, 0, 0, 0.01, 0.04, 0.09, 0.1, 0.05, 0.01, 0, 0, 0, 0, 0])
    res = (4, 10)
    assert_array_equal(spcutil.find_peak_edges(inp), res)

    inp = np.array([0.09, 0.1, 0.05, 0.01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0.04])
    res = (0, 4)
    assert_array_equal(spcutil.find_peak_edges(inp), res)


def test_scale_spectra():
    assert spcutil.scale_spectra(1, 540) == 4
    assert spcutil.scale_spectra(1, 539) == 2
