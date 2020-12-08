#!/usr/bin/env python3
import os
import argparse
from rpgpy import read_rpg
import pytest
from tempfile import NamedTemporaryFile
import pickle
from rpgpy import rpg2nc


def main():
    data_path = 'tests/data/level1/'
    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            data_file = NamedTemporaryFile(suffix='.pkl')
            with open(data_file.name, 'wb') as f:
                pickle.dump(data, f)

            assert str(header['FileCode']) in folder

            pytest.main(['-v', 'tests/e2e/level1/l1_tests.py',
                         f"--data={data_file.name}"])

            output_file = NamedTemporaryFile()
            rpg2nc(f'{os.path.join(data_path, folder)}/*.LV1', output_file.name,
                   global_attr={'foo': 'bar'})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level1 end-to-end tests.')
    ARGS = parser.parse_args()
    main()
