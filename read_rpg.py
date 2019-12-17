import reader
import rpg_header
import time

file_name = '191108_030000_P10_ZEN.LV0'
#file_name = 'joyrad94_20191108120000_P01_ZEN.lv0'

start = time.time()
header, _ = rpg_header.read_rpg_header(file_name)
res = reader.read_bytes(file_name, header)
end = time.time()
print(end-start)

