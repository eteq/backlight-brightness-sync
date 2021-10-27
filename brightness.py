#!/usr/bin/env python

import os
import sys
import subprocess

target_monitor = 'U2719D'
backlight_rescaling = 2

# see calibrations.ipynb for this constant
a, b = 0.21182376905860953*backlight_rescaling, 0.037511653943657866
def xl(xr, ml=2047, mr=100):
    return (ml/mr)*a*xr + ml * b

if len(sys.argv) != 2:
    print('Must give only brightness as argument')

busnum = None
if f'BUSNUM_{target_monitor}' in os.environ:
    busnum = int(os.environ[f'BUSNUM_{target_monitor}'])
else:
    busnum_filename = '/tmp/busnum_' + target_monitor

    if os.path.exists(busnum_filename):
        with open(busnum_filename) as f:
            busnum = int(f.read().strip())
        print('Found bus number', busnum, 'at', busnum_filename)
    else:
        out = subprocess.check_output('ddcutil detect', shell=True)
        lines = out.decode().split('\n')
        busnum = None
        for ln in lines:
            if 'I2C bus' in ln:
                busnum = int(ln.split('i2c-')[1].strip())
            if target_monitor in ln:
                print('Found', target_monitor, 'at bus number', busnum)
                break
        else:
            busnum = None

        if busnum is None:
            print('Failed to detect', target_monitor)
            sys.exit(1)

        print('Writing bus number to', busnum_filename)
        with open(busnum_filename, 'w') as fw:
            fw.write(str(busnum))

brightness_target = int(sys.argv[1])
if not (0 <= brightness_target <= 100):
    print('Brightness must be between 0 and 100 inclusive')
    sys.exit(2)

backlight_target = round(xl(brightness_target))
with open('/sys/class/backlight/intel_backlight/max_brightness') as f:
    max_backlight = int(f.read().strip())
backlight_target = max_backlight if backlight_target > max_backlight else backlight_target

print('Setting backlight to', backlight_target)
#with open('/sys/class/backlight/intel_backlight/brightness', 'w') as fw:
#    fw.write(str(backlight_target))
subprocess.check_call(f'echo {backlight_target} | sudo tee /sys/class/backlight/intel_backlight/brightness > /dev/null', shell=True)

print('Setting', target_monitor, 'to', brightness_target)
subprocess.check_call(f'ddcutil -b {busnum} setvcp 0x10 {brightness_target}', shell=True)
