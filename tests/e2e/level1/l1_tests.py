import pytest
from rpgpy import utils
import pickle
import numpy as np


class TestRpgPy:

    @pytest.fixture(autouse=True)
    def _fetch_params(self, params):
        self.data = self._read(params['data'])

    @staticmethod
    def _read(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    @pytest.mark.level0
    @pytest.mark.level1
    def test_time_vector(self):
        time = self.data['Time']
        t0 = utils.rpg_seconds2date(time[0])[:4]
        for t in time:
            assert t > 0
            assert utils.rpg_seconds2date(t)[:4] == t0

    @pytest.mark.level1
    def test_no_negative_Ze_values(self):
        assert np.all(self.data['Ze'] >= 0)
