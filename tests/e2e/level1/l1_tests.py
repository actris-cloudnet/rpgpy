import pickle

import numpy as np
import pytest

from rpgpy import utils


class TestRpgPy:
    data = None

    @pytest.fixture(autouse=True)
    def _fetch_params(self, params):
        self.data = self._read(params["data"])

    @staticmethod
    def _read(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)  # noqa: S301

    @pytest.mark.level0()
    @pytest.mark.level1()
    def test_time_vector(self):
        assert self.data is not None
        time = self.data["Time"]
        datetimes = utils.rpg_seconds2datetime64(time)
        dates = np.unique(datetimes.astype("datetime64[D]"))
        assert len(dates) == 1

    @pytest.mark.level1()
    def test_no_negative_Ze_values(self):
        assert self.data is not None
        assert np.all(self.data["Ze"] >= 0)
