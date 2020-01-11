from serial import Serial
from serial.tools.list_ports import comports

# this defines the baud rate of transmission and the device you want to connect to
device_num = 0
BAUD_RATE = 115200 

# get the available com device ports
ports = comports()

# make sure the one we want is there
assert(len(ports) > device_num, "The device {} specified was not found".format(device_num))

# create device
device = Serial(port=ports[device_num], baudrate=BAUD_RATE)
# print the port selected and the device object
print("Initialized with device " + str(ports[0]))
print(device)

# device has a method read_all which will give you everything currently in the stream
print(device.read_all())
