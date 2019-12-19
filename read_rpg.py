import os
import rpg_cython
import time

directory = 'data/'

for file in os.listdir(directory):
    start = time.time()
    header, data = rpg_cython.read_rpg(os.path.join(directory, file))
    end = time.time()
    print(end-start)
