import reader
import time

files = ['191108_030000_P10_ZEN.LV0',
         '191108_100002_P10_ZEN.LV0',
         'joyrad94_20191108120000_P01_ZEN.lv0',
         'joyrad94_20191108000001_P01_ZEN.lv0',
         '190823_090000_P10_ZEN.LV1']

for file in files:
    start = time.time()
    res = reader.read_rpg(f"data/{file}")
    end = time.time()
    print(end-start)

