import os
import reader
import time

directory = 'data/'

for file in os.listdir(directory):
    start = time.time()
    header, data = reader.read_rpg(os.path.join(directory, file))
    end = time.time()
    print(end-start)
