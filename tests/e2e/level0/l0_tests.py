import pytest
import netCDF4


class TestRpgPy:

    @pytest.fixture(autouse=True)
    def _fetch_params(self, params):
        self.filename = params['filename']

    def test_global_attributes(self):
        nc = netCDF4.Dataset(self.filename)
        attrs = ('year', 'month', 'day', 'uuid', 'history', 'foo')
        for attr in attrs:
            assert hasattr(nc, attr)
        nc.close()
