import matplotlib.pyplot as plt
from DataStream import DataStream

def main():
	ds = DataStream()
	data = ds.getAllData(300)
	data = ds.getAllData(300)
	data = ds.getAllData(300)

	x, y, z = data['time'], data['voltage'], data['current']

	plt.plot(x, y)
	plt.axis([0, 100, 0, 100])
	plt.xlabel('Time (s)')
	plt.ylabel('Voltage (V)')
	plt.title('Test graph')
	plt.grid()
	plt.axes([0, 1, 0, 1])
	plt.xticks([])
	plt.yticks([])

	# plt.show()

	return plt