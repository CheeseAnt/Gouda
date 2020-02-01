import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from dash import Dash
from dash.dependencies import Input, Output, State
from json import loads

from DataStream import DataStream

app = Dash(__name__)
ds = DataStream(debug=True)

def createInterval(interval=1000):
	return dcc.Interval(id="live-interval", interval=interval)

def createPlot(initial, title, xlabel, ylabel, **kwargs):
	plot = px.line(initial, x=xlabel, y=ylabel, title=title, **kwargs)

	return plot

main_plot = createPlot(pd.DataFrame(ds.getAllData()), "Voltage over Time", "time", "voltage")
app.layout = html.Div([
	dbc.Jumbotron("Measurements"),
	dcc.Graph(id="main-graph"),
	createInterval(500)])

@app.callback(
	Output("main-graph", "figure"),
	[Input("live-interval", "n_intervals")])
def updateMainPlot(n_intervals):
	new_data = ds.getAllData(100)
	main_plot.data[0].x = new_data['time']
	main_plot.data[0].y = new_data['voltage']

	return loads(main_plot.to_json())

if __name__ == '__main__':
	app.run_server(debug=True)
