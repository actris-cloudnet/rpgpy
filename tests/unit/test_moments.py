import os
from time import time

import numpy as np
from numpy.testing import assert_array_almost_equal

from rpgpy import read_rpg, spcutil, spectra2moments

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestFindPeaks:
    @staticmethod
    def test_main_peak_1():
        data = np.array([0, 0, 0, 0.3, 0, 0, 0.2, 0.3, 0.5, 0.2, 0, 0, 0, 0.2])
        ind_left, ind_right = spcutil.find_peak_edges(data)
        assert ind_left == 6
        assert ind_right == 10

    @staticmethod
    def test_find_single_value():
        data = np.array([0, 0, 0, 0.3, 0, 0])
        ind_left, ind_right = spcutil.find_peak_edges(data)
        assert ind_left == 3
        assert ind_right == 4

    @staticmethod
    def test_find_left_edge():
        data = np.array([0.1, 0.2, 0.3, 0.5, 0, 0])
        ind_left, ind_right = spcutil.find_peak_edges(data)
        assert ind_left == 0
        assert ind_right == 4

    @staticmethod
    def test_find_right_edge():
        data = np.array([0, 0.2, 0.3, 0.5, 0.4, 0.3])
        ind_left, ind_right = spcutil.find_peak_edges(data)
        assert ind_left == 1
        assert ind_right == 6  # is this OK, or should be 5 ?

    @staticmethod
    def test_find_peak_with_secondary_peak():
        data = np.array([0, 0.1, 0.3, 0.2, 0.35, 0.5, 0.3, 0.1, 0])
        ind_left, ind_right = spcutil.find_peak_edges(data)
        assert ind_left == 1
        assert ind_right == 8


class TestMoments:
    input_file = f"{FILE_PATH}/../data/level0/v3-889346/200704_000002_P10_ZEN.LV0"
    header, data = read_rpg(input_file)
    source_data_mean = np.mean(data["TotSpec"])
    start = time()
    moments = spectra2moments(data, header)
    stop = time()
    print("")
    print(f"Time elapsed: {stop - start} seconds")

    def test_header(self):
        assert self.header["SWVersion"] == 525
        assert self.header["FileCode"] == 889346

    def test_that_does_not_alter_input_data(self):
        assert_array_almost_equal(self.source_data_mean, np.mean(self.data["TotSpec"]))

    def test_that_we_get_the_reference_value(self):
        moments = spectra2moments(self.data, self.header, n_points_min=1)
        assert round(np.mean(moments["Ze"][moments["Ze"] > 0] * 1e5), 2) == 10.56

    def test_that_moments_contain_no_nans(self):
        for _, data in self.moments.items():
            assert bool(np.isnan(data).any()) is False

    def test_that_works_with_hspec(self):
        spectra2moments(self.data, self.header, spec_var="HSpec")


def test_spectral_ldr():
    input_file = f"{FILE_PATH}/../data/level0/v3-889346/190912_060003_P05_ZEN.LV0"
    header, data = read_rpg(input_file)
    spcutil.calc_spectral_LDR(header, data)
