#!/usr/bin/env python3
import os
import argparse
import pytest
from rpgpy import rpg2nc, read_rpg, utils
import sys
import numpy as np
import matplotlib.pyplot as plt


def main():
    data_path = 'tests/data/level1/'
    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)

        #pytest.main(['-v', 'tests/e2e/tests.py'])


def rm_file(fname):
    try:
        os.remove(fname)
    except OSError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level1 end-to-end tests.')
    ARGS = parser.parse_args()
    main()
