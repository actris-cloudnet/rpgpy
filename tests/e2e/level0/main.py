#!/usr/bin/env python3
import os
import argparse
import pytest
from rpgpy import rpg2nc, read_rpg
import numpy as np


def main():

    data_path = 'tests/data/level0/'

    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            assert str(header['FileCode']) in folder

            pytest.main(['-v', 'tests/e2e/level1/l1_tests.py',
                         f"--time={data['Time'][0::10]}",
                         f"--positive_Ze={np.all(data['TotSpec'] >= 0)}"])

        output_file = f'{data_path}rpg_file.nc'
        rm_file(output_file)
        rpg2nc(f'{os.path.join(data_path, folder)}/*.LV0', output_file, global_attr={'foo': 'bar'})
        pytest.main(['-v', 'tests/e2e/level0/l0_tests.py', f'--filename={output_file}'])
        rm_file(output_file)


def rm_file(fname):
    try:
        os.remove(fname)
    except OSError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level 0 end-to-end test.')
    ARGS = parser.parse_args()
    main()
