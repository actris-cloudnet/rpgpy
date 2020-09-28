#!/usr/bin/env python3
import os
import argparse
from rpgpy import read_rpg
import numpy as np
import pytest


def main():
    data_path = 'tests/data/level1/'
    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            assert str(header['FileCode']) in folder

            pytest.main(['-v', 'tests/e2e/level1/l1_tests.py',
                         f"--time={data['Time']}",
                         f"--positive_Ze={np.all(data['Ze'] >= 0)}"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level1 end-to-end tests.')
    ARGS = parser.parse_args()
    main()
