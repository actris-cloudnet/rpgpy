import numpy as np
from rpgpy import data
from numpy.testing import assert_array_equal


class TestMaskZeros:

    def test_masking_works_with_2d(self):
        x = np.array([[1, 0, 2], [0, 0, 2]])
        expected_mask = [[0, 1, 0], [1, 1, 0]]
        result = data._mask_zeros({'x': x})
        assert_array_equal(result['x'].data, x)
        assert_array_equal(result['x'].mask, expected_mask)

    def test_does_not_mask_vectors(self):
        x = np.array([1, 2, 3, 0])
        result = data._mask_zeros({'x': x})
        assert_array_equal(result['x'].data, x)
        assert hasattr(result['x'], 'mask') is False
