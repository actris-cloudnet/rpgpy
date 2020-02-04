import os
import rpgpy
import time
import matplotlib.pyplot as plt

file = '../data/hyde2/191216_150001_P10_ZEN.LV1'

#for file in os.listdir(directory):
start = time.time()
#    if file.endswith('0'):
#        print(file)
header, data = rpgpy.read_rpg(file)
end = time.time()
print(end-start)
