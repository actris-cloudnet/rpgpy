import os
from rpgpy import read_rpg, rpg2nc, rpg2nc_multi, spectra2nc
import rpgpy.nc
import pytest
import netCDF4
import glob

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestSTSRMode:

    expected_long_name = 'Differential Reflectivity Ratio'

    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        self.output_file = f'{FILE_PATH}/output.nc'
        self.input_file = f'{FILE_PATH}/../data/misc/BaseN_210913_001152_P01_PPI.LV1'
        yield
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_binary_file_reading(self):
        header, data = read_rpg(self.input_file)
        assert header['DualPol'] == 2

    def test_binary_file_reading_2(self):
        header, data = read_rpg(self.input_file, rpg_names=False)
        assert self.expected_long_name in data

    def test_converted_netcdf(self):
        rpg2nc(self.input_file, self.output_file)
        nc = netCDF4.Dataset(self.output_file)
        assert 'ldr' not in nc.variables
        assert 'zdr' in nc.variables
        assert nc.variables['zdr'].long_name == self.expected_long_name
        assert hasattr(nc, 'rpgpy_version')
        nc.close()


class TestLDRMode:

    expected_long_name = 'Linear Depolarisation Ratio'

    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        self.input_file = f'{FILE_PATH}/../data/misc/210929_070000_P09_ZEN.LV1'
        self.output_file = f'{FILE_PATH}/output.nc'
        yield
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_binary_file_reading(self):
        header, data = read_rpg(self.input_file)
        assert header['DualPol'] == 1

    def test_binary_file_reading_2(self):
        header, data = read_rpg(self.input_file, rpg_names=False)
        assert self.expected_long_name in data

    def test_converted_netcdf(self):
        rpg2nc(self.input_file, self.output_file)
        nc = netCDF4.Dataset(self.output_file)
        assert 'zdr' not in nc.variables
        assert 'ldr' in nc.variables
        assert nc.variables['ldr'].long_name == self.expected_long_name
        nc.close()


class TestSpectra2Nc:

    input_file = f'{FILE_PATH}/../data/level0/v3-889346/200704_000002_P10_ZEN.LV0'

    def test_netcdf_creation(self):
        output_file = f'{FILE_PATH}/../data/level0/v3-889346/output.nc'
        spectra2nc(self.input_file, output_file, global_attr={'location': 'Hyytiala'})
        nc = netCDF4.Dataset(output_file)
        expected_shape = (len(nc.variables['time']), len(nc.variables['range_layers']))
        for key in ('Ze', 'v', 'width', 'kurtosis', 'skewness'):
            assert key in nc.variables
            assert nc.variables[key].shape == expected_shape
        assert 'time' in nc.variables
        assert nc.location == 'Hyytiala'
        nc.close()
        os.remove(output_file)


class TestStationNameReading:

    def test_valid_customer_name(self):
        self.input_file = f'{FILE_PATH}/../data/misc/210929_070000_P09_ZEN.LV1'
        header, data = read_rpg(self.input_file)
        assert header['CustName'] == 'ESA 1'

    def test_invalid_customer_name(self):
        self.input_file = f'{FILE_PATH}/../data/misc/joyrad94_20210925000001_P01_ZEN.lv1'
        header, data = read_rpg(self.input_file)
        assert header['CustName'] == 'Univ. Cologne (J%lich)'


class TestRpg2ncMulti:

    cwd = os.getcwd()
    input_file_path = f'{FILE_PATH}/../data/misc/'
    input_files = glob.glob(f'{input_file_path}/*')

    def test_with_explicit_path(self):
        rpg2nc_multi(file_directory=self.input_file_path)
        for file in self.input_files:
            expected_filename = f'{self.cwd}/{os.path.basename(file)}.nc'
            assert os.path.exists(expected_filename)
            nc = netCDF4.Dataset(expected_filename)
            nc.close()
            os.remove(expected_filename)

    def test_return_value(self):
        filenames = rpg2nc_multi(file_directory=self.input_file_path)
        assert len(filenames) == len(self.input_files)
        for file in filenames:
            assert os.path.exists(file)
            os.remove(file)

    def test_basename(self):
        basename = 'foo'
        rpg2nc_multi(file_directory=self.input_file_path, base_name=basename)
        for file in self.input_files:
            expected_filename = f'{self.cwd}/{basename}_{os.path.basename(file)}.nc'
            assert os.path.exists(expected_filename)
            os.remove(expected_filename)

    def test_default_directory(self):
        os.chdir(f'{FILE_PATH}/../data/misc/')
        cwd = os.getcwd()
        rpg2nc_multi()
        for file in self.input_files:
            expected_filename = f'{cwd}/{os.path.basename(file)}.nc'
            assert os.path.exists(expected_filename)
            os.remove(expected_filename)
        assert glob.glob(f'{cwd}/*.nc') == []

    def test_output_dir(self):
        output_dir = f'{FILE_PATH}/../data/level0/v3-889346/'
        rpg2nc_multi(file_directory=self.input_file_path, output_directory=output_dir)
        for file in self.input_files:
            expected_filename = f'{output_dir}/{os.path.basename(file)}.nc'
            assert os.path.exists(expected_filename)
            os.remove(expected_filename)

    def test_recursive(self):
        input_dir = f'{FILE_PATH}/../data/'
        output_dir = f'{FILE_PATH}/../data/level0/v3-889346/'
        files = rpg2nc_multi(file_directory=input_dir, output_directory=output_dir, recursive=False)
        assert len(files) == 0
        input_dir = f'{FILE_PATH}/../data/misc/'
        files = rpg2nc_multi(file_directory=input_dir, output_directory=input_dir, recursive=False)
        assert len(files) == 3
        for file in files:
            os.remove(file)


class TestGeneratorFiles:

    dir_name = f'{FILE_PATH}/../data/'
    lv1 = ('.lv1', '.LV1')
    lv0 = ('.lv0', '.LV0')

    def test_lv1(self):
        files = rpgpy.nc._generator_files(self.dir_name, False, True)
        files = [file for file in files]
        for file in files:
            assert not file.endswith(self.lv0)
            assert file.endswith(self.lv1)
            assert os.path.exists(file)
        assert len(files) >= 6

    def test_lv1_and_lv0(self):
        files = rpgpy.nc._generator_files(self.dir_name, True, True)
        files = [file for file in files]
        for file in files:
            assert file.endswith(self.lv1 + self.lv0)
            assert os.path.exists(file)
        assert len(files) >= 7
