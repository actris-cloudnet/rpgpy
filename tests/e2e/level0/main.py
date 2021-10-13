#!/usr/bin/env python3
import os
import argparse
import subprocess
import pytest
from rpgpy import rpg2nc_multi, rpg2nc, read_rpg
from tempfile import NamedTemporaryFile
import pickle


def main():

    data_path = 'tests/data/level0/'

    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            assert str(header['FileCode']) in folder

            data_file = NamedTemporaryFile(suffix='.pkl')
            with open(data_file.name, 'wb') as f:
                d = {
                    'Time': data['Time'],
                }
                pickle.dump(d, f)

            pytest.main(['-v', 'tests/e2e/level1/l1_tests.py',
                         '-m', 'level0',
                         f"--data={data_file.name}"])
        global_attr = {'foo': 'bar'}

        output_file = NamedTemporaryFile()
        rpg2nc(f'{os.path.join(data_path, folder)}/*.LV0', output_file.name,
               global_attr=global_attr)
        pytest.main(['-v', 'tests/e2e/level0/l0_tests.py', f'--filename={output_file.name}'])

        base_name = 'test'
        rpg2nc_multi(data_path, base_name=base_name, global_attr=global_attr)

        for subdir, dirs, files in sorted(os.walk('.')):
            for file in files:
                if file.startswith(base_name) and file.endswith('.nc'):
                    pytest_args = ['pytest', '-v', 'tests/e2e/level0/l0_tests.py',
                                   f'--filename={file}']
                    try:
                        subprocess.check_call(pytest_args)
                    except subprocess.CalledProcessError:
                        raise

        # cleaning up the project folder
        os.system("rm *.nc")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level 0 end-to-end test.')
    ARGS = parser.parse_args()
    main()
