import numpy as np

""" Provides data in a "stream" """
class DataStream:

	""" Holds a measurement value and time """
	class Measurement:
		def __init__(self, time_, value_):
			self.t = time_
			self.v = value_

	def __init__(self):
		# outstanding values that have just come in
		self.current = list()
		self.voltage = list()
		self.power = list()

		# total history that has been read
		self.current_history = list()
		self.voltage_history = list()
		self.power_history = list()

	def measurementsFromList(values, times = None):
		measurements = list()
		
		# check if values holds both time and value
		if times is None:
			if isinstance(values, np.ndarray):
				assert(values.shape[1] == 2, "No times provided with measurements")

				for x in range(len(values[:, 0])):
					list.append(Measurement(values[x, 0], values[x, 1]))
			else
				assert(False, "No times provided with measurements")
		# else they are separate
		else:
			# ensure both vectors are same length
			assert(len(values) == len(times))

			for x in range(len(values)):
				list.append(Measurement(values[x], times[x]))

		return measurements

	# pull in measurements from arduino
	# TODO actually pull in the measurements
	def updateMeasurements(self):
		from random import random
		update_size = round(random()*20)

		self.current.extend(
			self.measurementsFromList(np.random.random((update_size, 2))*10))

		self.voltage.extend(
			self.measurementsFromList(np.random.random((update_size, 2))*50))

		self.power.extend(
			self.measurementsFromList(np.random.random((update_size, 2))*500))

	def getNewData(self):
		self.updateMeasurements()

		# update totals
		self.current_history.extend(self.current)
		self.voltage_history.extend(self.voltage)
		self.power_history.extend(self.power)

		# return data in dictionary
		results = dict()

		# use copy to stop dictionary contents being deleted also
		results.update({'current' : self.current.copy()})
		self.current.clear()

		results.update({'voltage' : self.voltage.copy()})
		self.voltage.clear()

		results.update({'power' : self.power.copy()})
		self.power.clear()

		return results

	def getAllData(self):
		self.getNewData()

		# return data in dictionary
		results = dict()

		# use copy to stop dictionary contents being deleted also
		results.update({'current' : self.current_history})
		results.update({'voltage' : self.voltage_history})
		results.update({'power' : self.power_history})
		
		return results		