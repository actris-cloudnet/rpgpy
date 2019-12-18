import reader
import time

files = ['191108_030000_P10_ZEN.LV0',
         'joyrad94_20191108120000_P01_ZEN.lv0',
         'joyrad94_20191108000001_P01_ZEN.lv0']
         

for file in files:
    start = time.time()
    res = reader.read_rpg_l0(f"data/{file}")
    end = time.time()
    print(end-start)

