import time
import board
import adafruit_tsl2591
from PIL import Image

i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

im = Image.new('RGB', (500, 500), (255,255,255))
im.show()


out = ''
while out == '':
    out = input(f'lux is {sensor.lux}. Type anything other than enter to continue:')


with open('/sys/class/backlight/intel_backlight/max_brightness') as f:
    mx = int(f.read().strip())

with open('/sys/class/backlight/intel_backlight/brightness') as f:
    start_level = f.read().strip()

print('started at', start_level)

n = 21
perc = []
lux = []
with open('/sys/class/backlight/intel_backlight/brightness', 'w') as fw:
    for i in range(n):
        perc.append(i/(n-1))
        l = int(mx * perc[-1])
        print('setting to', l)
        fw.write(str(l))
        fw.flush()
        time.sleep(.75)
        lux.append(sensor.lux)
        print('perc', perc[-1],'at', lux[-1],'lux')
    fw.write(start_level)

ofn = 'brightness_backlight_calibration'
print('Writing', ofn)
with open(ofn, 'w') as f:
    f.write('backlight_frac lux\n')
    for p, l in zip(perc, lux):
        f.write(f'{p} {l}\n')



