#!/usr/bin/env python3
import argparse
import os
import pickle
import subprocess
from tempfile import NamedTemporaryFile

import pytest

from rpgpy import read_rpg, rpg2nc, rpg2nc_multi


def main():
    data_path = "tests/data/level1/"
    for folder in os.listdir(data_path):  # pylint: disable=R1702
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            data_file = NamedTemporaryFile(suffix=".pkl")  # pylint: disable=R1732
            with open(data_file.name, "wb") as f:
                pickle.dump(data, f)

            assert str(header["FileCode"]) in folder

            pytest.main(["-v", "tests/e2e/level1/l1_tests.py", f"--data={data_file.name}"])

            global_attr = {"foo": "bar"}

            output_file = NamedTemporaryFile()  # pylint: disable=R1732
            rpg2nc(
                f"{os.path.join(data_path, folder)}/{file}",
                output_file.name,
                global_attr=global_attr,
            )

            pytest.main(["-v", "tests/e2e/level0/l0_tests.py", f"--filename={output_file.name}"])

            base_name = "test"
            rpg2nc_multi(data_path, base_name=base_name, include_lv0=False, global_attr=global_attr)

            for _, _, files in sorted(os.walk(".")):
                for nc_file in files:
                    if file.startswith(base_name) and file.endswith(".nc"):
                        pytest_args = [
                            "pytest",
                            "-v",
                            "tests/e2e/level1/l1_tests.py",
                            f"--filename={nc_file}",
                        ]
                        try:
                            subprocess.check_call(pytest_args)
                        except subprocess.CalledProcessError:  # pylint: disable=W0706
                            raise

            # cleaning up the project folder
            os.system("rm *.nc")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RpgPy Level1 end-to-end tests.")
    ARGS = parser.parse_args()
    main()
