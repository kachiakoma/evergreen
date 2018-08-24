from control import control
import time

# Create controler object
controler = control()

# Get current switch state for sensor A and print
switch = controler.read_sensorA()
print('Switch A: {0}'.format(switch))

# Blink LED
print("Blinking LED (Ctrl + C to stop)...")
while True:
    controler.write_deviceA(True)
    time.sleep(0.5)
    controler.write_deviceA(False)
    time.sleep(0.5)

