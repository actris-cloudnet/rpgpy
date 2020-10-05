from rpgpy import utils
from numpy.testing import assert_array_equal


def test_rpg_seconds2date():
    date = utils.rpg_seconds2date(0)
    date_only = utils.rpg_seconds2date(0, date_only=True)
    res = ['2001', '01', '01', '00', '00', '00']
    assert_array_equal(date, res)
    assert_array_equal(date_only, res[:3])
