import re
import os
import subprocess
import time
import board
import adafruit_tsl2591
from PIL import Image

i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

print('showing ddcutil detect output')
os.system('ddcutil detect')

im = Image.new('RGB', (500, 500), (255,255,255))
im.show()

out = ''
while out == '':
    out = input(f'lux is {sensor.lux}. Type the appropriate bus number to continue or enter to read out the lux more:')

busnum = int(out)
print('Using bus #', busnum)

out = subprocess.check_output(f'ddcutil -b {busnum} getvcp 0x10', shell=True)
match = re.match('.*:(.*)=(.*), (.*)=(.*)', out.decode().strip())
curr = int(match.group(2))
mx = int(match.group(4))

print('started at', curr)

n = 21
perc = []
lux = []

for i in range(n):
    perc.append(i/(n-1))
    l = int(mx * perc[-1])
    print('setting to', l)

    subprocess.check_call(f'ddcutil -b {busnum} setvcp 0x10 {l}', shell=True)

    time.sleep(.75)
    lux.append(sensor.lux)
    print('perc', perc[-1],'at', lux[-1],'lux')
subprocess.check_call(f'ddcutil -b {busnum} setvcp 0x10 {curr}', shell=True)

ofn = 'brightness_dcc_calibration'
print('Writing', ofn)
with open(ofn, 'w') as f:
    f.write('backlight_frac lux\n')
    for p, l in zip(perc, lux):
        f.write(f'{p} {l}\n')



