from serial import Serial
from serial.tools.list_ports import comports

device_num = 0
BAUD_RATE = 115200 

ports = comports()
assert(len(ports) > device_num)

# create device
device = Serial(port=ports[device_num], baudrate=BAUD_RATE)

print("Initialized with device " + str(ports[0]))
print(device)

