from rpgpy import utils, spcutil
import numpy as np
from numpy.testing import assert_array_equal
import pytest


def test_rpg_seconds2date():
    date = utils.rpg_seconds2date(0)
    date_only = utils.rpg_seconds2date(0, date_only=True)
    res = ['2001', '01', '01', '00', '00', '00']
    assert_array_equal(date, res)
    assert_array_equal(date_only, res[:3])


@pytest.mark.parametrize("input, result", [
    (0, ['2001', '01', '01', '00', '00', '00']),
    (24*60*60*10 + 1, ['2001', '01', '11', '00', '00', '01']),
    (24*60*60 - 1, ['2001', '01', '01', '23', '59', '59']),
    (625107602, ['2020', '10', '23', '01', '00', '02'])
])
def test_seconds2date(input, result):
    assert utils.rpg_seconds2date(input) == result


def test_create_velocity_vectors():
    inp = {'SpecN': [20], 'MaxVel': [10], 'SequN': 1}
    res = [[-9.5, -8.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5,  0.5,
            1.5,  2.5,  3.5, 4.5,  5.5,  6.5,  7.5, 8.5,  9.5]]
    assert_array_equal(utils.create_velocity_vectors(inp), res)

    inp = {'SpecN': [4, 10], 'MaxVel': [8, 5], 'SequN': 2}
    res = [[0, 0, 0, -6, -2, 2, 6, 0, 0, 0],
           [-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5]]
    mask = [[1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    assert_array_equal(utils.create_velocity_vectors(inp), res)
    assert_array_equal(utils.create_velocity_vectors(inp).mask, mask)


def test_find_peak_edges():
    inp = np.array([0, 0, 0, 0, 0.01, 0.04, 0.09, 0.1, 0.05, 0.01, 0, 0, 0, 0, 0])
    res = (4, 10)
    assert_array_equal(spcutil.find_peak_edges(inp), res)

    inp = np.array([0.09, 0.1, 0.05, 0.01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0.04])
    res = (0, 4)
    assert_array_equal(spcutil.find_peak_edges(inp), res)
