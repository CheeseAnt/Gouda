import numpy as np

""" Provides data in a 'stream' """
class DataStream:
	def __init__(self, device=0):
		# initiate serial
		self.initializeCommunication(device)
		
		# outstanding values that have just come in
		self._current = list()
		self._voltage = list()
		self._power = list()
		self._time = list()

		# total history that has been read
		self._current_history = list()
		self._voltage_history = list()
		self._power_history = list()
		self._time_history = list()

	def _measurementsFromArray(self, values):
		# check that array is 1-D
		assert(len(values.shape) == 1, 'Measurements are not 1-D')

		measurements = list()
		for x in range(len(values)):
			measurements.append(float(values[x]))

		return measurements

	# TODO actually pull in the measurements
	def _updateMeasurements(self):
		""" get all recent measurements from device """
		from random import random
		update_size = round(random()*20)

		self._current.extend(
			self._measurementsFromArray(np.random.random((update_size))*10))

		self._voltage.extend(
			self._measurementsFromArray(np.random.random((update_size))*50))

		self._power.extend(
			self._measurementsFromArray(np.random.random((update_size))*500))

		self._time.extend(
			self._measurementsFromArray(np.array([x for x in range(len(self._time_history), len(self._time_history) + update_size)])))

	def getNewData(self):
		""" get updated measurements from device and return all recent """
		self._updateMeasurements()

		# update totals
		self._current_history.extend(self._current)
		self._voltage_history.extend(self._voltage)
		self._power_history.extend(self._power)
		self._time_history.extend(self._time)

		# return data in dictionary
		results = dict()

		# use copy to stop dictionary contents being deleted also
		results.update({'current' : np.array(self._current.copy())})
		self._current.clear()

		results.update({'voltage' : np.array(self._voltage.copy())})
		self._voltage.clear()

		results.update({'power' : np.array(self._power.copy())})
		self._power.clear()

		results.update({'time' : np.array(self._time.copy())})
		self._time.clear()

		return results

	def getAllDataNoUpdate(self, last_n=0):
		""" return all data without updating from device, optionally only n data """
		# return data in dictionary
		results = dict()

		# use copy to stop dictionary contents being deleted also
		results.update({'current' : np.array(self._current_history[-last_n:])})
		results.update({'voltage' : np.array(self._voltage_history[-last_n:])})
		results.update({'power' : np.array(self._power_history[-last_n:])})
		results.update({'time' : np.array(self._time_history[-last_n:])})
		
		return results

	def getAllData(self, last_n=0):
		""" update data then return all """
		self.getNewData()

		return self.getAllDataNoUpdate(last_n)

	def initializeCommunication(self, device):
		""" begin serial comms with arduino or otherwise """
		print("Initialized with device " + str(device))