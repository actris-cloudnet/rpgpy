#!/usr/bin/env python3
import argparse
import os
import pickle
import subprocess

import pytest

from rpgpy import read_rpg, rpg2nc, rpg2nc_multi


def main():
    data_path = "tests/data/level1/"

    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

            assert str(header["FileCode"]) in folder

            data_file = "temp_filename.pkl"
            with open(data_file, "wb") as f:
                pickle.dump(data, f)

            pytest.main(["-v", "tests/e2e/level1/l1_tests.py", f"--data={data_file}"])

            global_attr = {"foo": "bar"}

            output_filename = "temp-file.nc"
            rpg2nc(
                f"{os.path.join(data_path, folder)}/{file}",
                output_filename,
                global_attr=global_attr,
            )

            pytest.main(
                ["-v", "tests/e2e/level0/l0_tests.py", f"--filename={output_filename}"]
            )

            base_name = "test"
            rpg2nc_multi(
                data_path,
                base_name=base_name,
                include_lv0=False,
                global_attr=global_attr,
            )

            for _, _, files in sorted(os.walk(".")):
                for nc_file in files:
                    if file.startswith(base_name) and file.endswith(".nc"):
                        pytest_args = [
                            "pytest",
                            "-v",
                            "tests/e2e/level1/l1_tests.py",
                            f"--filename={nc_file}",
                        ]
                        subprocess.check_call(pytest_args)

            # cleaning up the project folder
            os.system("rm *.nc")
            os.remove(data_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RpgPy Level1 end-to-end tests.")
    ARGS = parser.parse_args()
    main()
