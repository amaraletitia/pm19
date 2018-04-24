from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, FactorRange, DatetimeTickFormatter, HoverTool, Legend, LabelSet
from bokeh.plotting import figure
from bokeh.palettes import brewer, mpl, Inferno256, Viridis256, Spectral11,Category20c
from bokeh.transform import factor_cmap
import pandas as pd

class ChartVisualizer(object):
	def __init__(self, *args, **kwargs):
		super(ChartVisualizer, self).__init__(*args, **kwargs)

	def produce_bar(self, df, sort_by=0, ascending=True):
		if isinstance(df, dict):
			df = pd.DataFrame(list(df.items()), columns=['x', 'count'])
		cols = df.columns
		df.sort_values(cols[sort_by], inplace=True, ascending=ascending)
		df[cols[0]]=df[cols[0]].astype(str)
		source = ColumnDataSource(df)


		#p.vbar(x=cols[0], top=cols[1], width=0.5, source=source,line_color='white', fill_color=factor_cmap(cols[0], palette=Spectral11, factors=df.index))
		TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
		if len(df[cols[0]]) < 20:
			p = figure(x_range=list(df[cols[0]]), plot_height=500, tools = TOOLS, toolbar_location='below', title="Counts")
			p.vbar(x=cols[0], top=cols[1], width=0.5, source=source, fill_color=factor_cmap(cols[0], palette=Category20c[19], factors=list(df[cols[0]])))
		else:
			p = figure(x_range=list(df[cols[0]]), sizing_mode='stretch_both', tools = TOOLS, toolbar_location='below', title="Counts")
			p.vbar(x=cols[0], top=cols[1], width=0.5, source=source)

		labels = LabelSet(x=cols[0], text=cols[1], y_offset=8,
                  text_font_size="10pt", text_color="#000000",
                  source=source, text_align='center')
		p.add_layout(labels)

		p.legend.orientation = "horizontal"
		p.legend.location = "top_center"
		show(p)

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

	def produce_pattern_analysis(self, eventlog, y, x):
		from math import pi
		import pandas as pd

		from bokeh.io import show
		from bokeh.models import (
		    ColumnDataSource,
		    HoverTool,
		    LinearColorMapper,
		    BasicTicker,
		    PrintfTickFormatter,
		    ColorBar,
		)
		from bokeh.plotting import figure
		pattern_table = eventlog.groupby([y, x]).CASE_ID.apply(list).apply(set).apply(len)

		xs = list(set(pattern_table.index.get_level_values(0)))
		print(xs)
		xs = [ int(x) for x in xs ]
		xs.sort()
		xs = [ str(x) for x in xs ]
		eqps = list(set(pattern_table.index.get_level_values(1)))
		eqps.sort()
		xs_count = eventlog.count_cluster()
		xs_count = xs_count.to_dict()
		for i in xs:
			#print(pattern_table.loc[pattern_table.index.get_level_values(0) == i])
			pattern_table.loc[pattern_table.index.get_level_values(0) == i] = pattern_table.loc[pattern_table.index.get_level_values(0) == i]/xs_count[i]*100
		pattern_table = pattern_table.to_frame()
		pattern_table.reset_index(inplace=True)
		pattern_table = pattern_table.rename(columns={'CASE_ID': 'rate'})
		colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
		mapper = LinearColorMapper(palette=colors, low=pattern_table.rate.min(), high=pattern_table.rate.max())

		source = ColumnDataSource(pattern_table)

		TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

		p = figure(title="Pattern Analysis of Cluster({0} ~ {1})".format(xs[0], xs[-1]),
		           x_range=eqps, y_range=xs,
		           x_axis_location="above", sizing_mode='stretch_both',
		           tools=TOOLS, toolbar_location='below')

		p.grid.grid_line_color = None
		p.axis.axis_line_color = None
		p.axis.major_tick_line_color = None
		p.axis.major_label_text_font_size = "10pt"
		p.axis.major_label_standoff = 0
		p.xaxis.major_label_orientation = pi / 3

		p.rect(x=x, y="Cluster", width=1, height=1,
		       source=source,
		       fill_color={'field': 'rate', 'transform': mapper},
		       line_color=None)

		color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
		                     ticker=BasicTicker(desired_num_ticks=len(colors)),
		                     formatter=PrintfTickFormatter(format="%d%%"),
		                     label_standoff=6, border_line_color=None, location=(0, 0))
		p.add_layout(color_bar, 'right')

		p.select_one(HoverTool).tooltips = [
		     (y, '@Cluster'),
		     (x, '@{}'.format(x)),
		     ('rate', '@rate%'),
		]

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

