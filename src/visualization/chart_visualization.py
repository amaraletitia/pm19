from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, FactorRange, DatetimeTickFormatter, HoverTool, Legend
from bokeh.plotting import figure
from bokeh.palettes import brewer, mpl, Inferno256, Viridis256

class ChartVisualizer(object):
	def __init__(self, *args, **kwargs):
		super(ChartVisualizer, self).__init__(*args, **kwargs)

	def produce_nested_bar(self, df):

		output_file("../result/bar_nested.html")

		TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

		index_0 = list(df.index.get_level_values(0))
		index_1 = list(df.index.get_level_values(1))

		x = [ (i_0, i_1) for i_0, i_1 in zip(index_0, index_1) ]
		_to_dict = dict(x=x ,counts=df.values)

		source = ColumnDataSource(data=dict(x=x, counts=df.values))

		p = figure(x_range=FactorRange(*x), sizing_mode='stretch_both', title="Basic Performance Analysis", tools=TOOLS)

		p.vbar(x='x', top='counts', width=0.9, source=source)

		p.y_range.start = 0
		p.x_range.range_padding = 0.1
		p.xaxis.major_label_orientation = 1
		p.xgrid.grid_line_color = None

		show(p)

	def produce_dotted_chart(self,eventlog, _type = 'ACTIVITY', _time = 'actual'):

		activities = eventlog.get_activities()
		TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"
		TOOLS = "pan,wheel_zoom,box_zoom,reset,save".split(',')
		eventlog['x_time'] = [x.strftime("%Y-%m-%d") for x in eventlog['TIMESTAMP']]

		hover = HoverTool(
			tooltips=[
			("CASE_ID", "@CASE_ID"),
			("ACTIVITY", "@ACTIVITY"),
			("RESOURCE", "@RESOURCE"),
			("TIMESTAMP", "@x_time"),
			]
		)
		TOOLS.append(hover)


		p = figure(tools = TOOLS, sizing_mode = 'stretch_both', title="Years vs mpg with jittering")

		# Get the colors for the boxes.

		colors = self.color_list_generator(eventlog, _type)
		eventlog['colors'] = colors



		source = ColumnDataSource(eventlog)
		if _time == 'actual':
			p.circle(x='TIMESTAMP', y='CASE_ID', source = source, color = 'colors', alpha=0.5, legend = _type)
			p.xaxis.formatter=DatetimeTickFormatter(
	        hours=["%d %B %Y"],
	        days=["%d %B %Y"],
	        months=["%d %B %Y"],
	        years=["%d %B %Y"])
		if _time == 'relative':
			p.circle(x='relative_time', y='CASE_ID', source = source, color = 'colors', alpha=0.5, legend = _type)


		p.legend.location = "top_left"
		#p.legend.click_policy="hide"
		show(p)




	def color_list_generator(self, df, treatment_col):
	    """ Create a list of colors per treatment given a dataframe and
	        column representing the treatments.

	        Args:
	            df - dataframe to get data from
	            treatment_col - column to use to get unique treatments.

	        Inspired by creating colors for each treatment
	        Rough Source: http://bokeh.pydata.org/en/latest/docs/gallery/brewer.html#gallery-brewer
	        Fine Tune Source: http://bokeh.pydata.org/en/latest/docs/gallery/iris.html
	    """
	    # Get the number of colors we'll need for the plot.
	    interval = int(256/len(df[treatment_col].unique()))
	    colors = [Viridis256[x] for x in range(255, 0, -interval)]
	    # Create a map between treatment and color.
	    colormap = {i: colors[k] for k,i in enumerate(df[treatment_col].unique())}
	    # Return a list of colors for each value that we will be looking at.
	    return [colormap[x] for x in df[treatment_col]]

