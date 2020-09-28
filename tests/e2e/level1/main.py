#!/usr/bin/env python3
import os
import argparse
from rpgpy import read_rpg


def main():
    data_path = 'tests/data/level1/'
    for folder in os.listdir(data_path):
        for file in os.listdir(os.path.join(data_path, folder)):
            filename = os.path.join(data_path, folder, file)
            header, data = read_rpg(filename)


def rm_file(fname):
    try:
        os.remove(fname)
    except OSError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RpgPy Level1 end-to-end tests.')
    ARGS = parser.parse_args()
    main()
