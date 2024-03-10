import wx
import matplotlib
import numpy as np
from DataStream import DataStream
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


def onClose(event):
	print("Closing app " + str(event))
	quit()

def updatePlot(event, fcanvas, axes, ds):
	# clear axes
	axes.cla()

	# get new data, plot and draw
	data = ds.getAllData(300)
	axes.plot(data['time'], data['voltage'])

	axes.set_xlabel('Time (s)')
	# axes.set_xticklabels([min(data['time']), max(data['time'])])
	# axes.set_xmargin([min(data['time']), max(data['time'])])
	
	xmax = 300 if max(data['time']) < 300 else max(data['time'])
	axes.set_xlim([min(data['time']), xmax])

	y_extremities = [min(data['voltage']), max(data['voltage'])]
	axes.set_ylim([y_extremities[0] - y_extremities[1] * 0.1, y_extremities[1] + y_extremities[1]*0.1])
	axes.set_ylabel('Voltage (V)')

	# axes.set_autoscale_on(True)
	fcanvas.draw()

app = wx.App()
frame = wx.Frame(None, -1, 'TestWx')
frame.SetSize(0, 0, 800, 450)
frame.Bind(wx.EVT_CLOSE, onClose)
frame.Centre()

fig = Figure()
fig.add_axes([0, 0, 1, 1])
ax = fig.add_subplot(111)
print(dir(ax))

dstream = DataStream(debug=True)

fcanvas = FigureCanvas(frame, -1, fig)
frame.Bind(wx.EVT_UPDATE_UI, lambda evt : updatePlot(evt, fcanvas, ax, dstream))
updatePlot('fakeevent', fcanvas, ax, dstream)

frame.Show()

app.MainLoop()
