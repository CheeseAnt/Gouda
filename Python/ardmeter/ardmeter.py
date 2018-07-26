import matplotlib as mpl
import numpy as np
import tkinter as tk
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg

def draw_figure(canvas, figure, loc=(0, 0)):
	""" draws a figure on the canvas with position relative
	to top left corner of canvas """

	# relate
	figure_canvas = FigureCanvasAgg(figure)
	figure_canvas.draw()
	
	# get dimensions
	_, _, f_w, f_h = figure.bbox.bounds
	f_w, f_h = int(f_w), int(f_h)

	# create photo
	photo = tk.PhotoImage(master=canvas, width=f_w, height=f_h)

	# slap onto canvas
	canvas.create_image(loc[0] + f_w/2, loc[1] + f_h/2, image=photo)
	tkagg.blit(photo, figure_canvas.get_renderer()._renderer, colormode=2)

	# keep photo object alive or else it will disappear
	return photo

# create canvas

w, h = 600, 400

window = tk.Tk()
window.title('ArdMeter')

canvas = tk.Canvas(window, width=w, height=h)
canvas.pack()

# data
# TODO : replace with arduino interaction
X = [0, 1, 2, 3, 4, 6, 10, 23]
Y = [3, 7, -1, 55, 2, 1, 0, 10]
fig = mpl.figure.Figure(figsize=(2, 1))
ax = fig.add_axes([0, 0, 1, 1])

#tk.mainloop() # use window.update_idletasks() and window.update() instead

from time import sleep
for i in range(10):
	X += np.int_(np.random.random(8)*10)
	Y += np.int_(np.random.random(8)*10)

	ax.plot(X, Y)

	# keep alive
	fig_photo = draw_figure(canvas, fig)

	#window.update_idletasks()
	window.update()

	sleep(0.2)
	ax.cla()