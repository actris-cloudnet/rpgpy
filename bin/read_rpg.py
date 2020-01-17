import os
import rpgpy
import time

directory = '../data/hyde/'

for file in os.listdir(directory):
    start = time.time()
    header, data = rpgpy.read_rpg(os.path.join(directory, file))
    end = time.time()
    print(end-start)
