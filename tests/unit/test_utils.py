from rpgpy import utils
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
    inp = {'SpecN': [20], 'MaxVel': [10]}
    res = [([-9.5, -8.5, -7.5, -6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5,  0.5, 1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5,
             8.5,  9.5])]
    assert_array_equal(utils.create_velocity_vectors(1, inp), res)
