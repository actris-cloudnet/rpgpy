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
