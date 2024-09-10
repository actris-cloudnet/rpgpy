import netCDF4
import pytest


class TestRpgPy:
    filename = ""

    @pytest.fixture(autouse=True)
    def _fetch_params(self, params):
        self.filename = params["filename"]

    def test_global_attributes(self):
        with netCDF4.Dataset(self.filename) as nc:
            attrs = ("year", "month", "day", "uuid", "history", "foo")
            for attr in attrs:
                assert hasattr(nc, attr)
