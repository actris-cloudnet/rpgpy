import pytest
from rpgpy import utils


def _arg_string_to_list(arg_string):
    return [int(x) for x in arg_string.strip('[').strip(']').split(' ')]


class TestRpgPy:

    @pytest.fixture(autouse=True)
    def _fetch_params(self, params):
        self.time = _arg_string_to_list(params['time'])
        self.positive_Ze = params['positive_Ze']

    def test_time_vector(self):
        assert self.time[0] > 0
        assert utils.rpg_seconds2date(self.time[0])[:4] == utils.rpg_seconds2date(self.time[-1])[:4]

    def test_no_negative_Ze_values(self):
        assert self.positive_Ze
