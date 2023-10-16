import streamlit as st
from streamlit_elements import elements, mui, html
import json
import random
from omnibelt import load_yaml
import streamlit as st
from pathlib import Path
import pandas as pd
# from stox import streamlit as lit
from stox import misc
from stox import load_symbol_table
# from stox.streamlit import Card, Portfolio
# from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo
from stox.general import DistributionLoader
import omnifig as fig


if 'sidebar_state' not in st.session_state:
	st.session_state.sidebar_state = 'expanded'
st.set_page_config(layout="wide", initial_sidebar_state=st.session_state.sidebar_state)

@st.cache_resource
def load_config():
	fig.initialize()
	return fig.create_config('app')
cfg = load_config()


def load_ticker(yfsym: str):
	container_source = cfg.peek('container')
	with container_source.silence():
		date = cfg.pull('date', 'last')
		date = str(date)
		ctx = container_source.create()
	ctx['ticker'] = yfsym
	ctx['date'] = date
	return ctx


@st.cache_resource
def load_cards():
	container_source = cfg.peek('container')
	def create_container(yfsym, date):
		with container_source.silence():
			ctx = container_source.create()
		ctx['ticker'] = yfsym
		ctx['date'] = date
		return ctx

	date = cfg.pull('date', 'last')
	date = str(date)

	tickers = cfg.pull('tickers', None)

	features = cfg.pull('features')
	if isinstance(features, dict):
		features = list(features.keys())

	infos = [create_container(yfsym, date) for yfsym in tickers[:40]] # testing
	# p = Portfolio()
	# p.populate([Card(info, features) for info in infos])
	# return p
# p = load_cards()

# @st.cache_resource
# def load_data():
# 	portfolio = cfg.pull('portfolio', None)
# 	pass


@st.cache_resource
def load_data(path: Path):
	if path.suffix == '.csv':
		return pd.read_csv(path)
	elif path.suffix == '.json':
		return pd.read_json(path)
	elif path.suffix == '.yaml':
		data = load_yaml(path)
		return pd.DataFrame(data)
	raise NotImplementedError

@st.cache_resource
def get_known_symbols():
	return load_symbol_table()
symbols_table = get_known_symbols()


def load_portfolio(name):
	loader = DistributionLoader(name=name)
	raw = loader.distributions




# path = misc.assets_root() / 'euro-stats.csv'

df = pd.read_csv(misc.assets_root() / 'euro-stats-sep28.csv')

edited_df = st.data_editor(df)


# p.display()







########################################################################################################################


# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').

# # Show title and description of the app.
# st.title('Example: Controlling sidebar programmatically')
# st.sidebar.markdown('This is an example Streamlit app to show how to expand and collapse the sidebar programmatically.')
#
# # Toggle sidebar state between 'expanded' and 'collapsed'.
# if st.button('Click to toggle sidebar state'):
# 	st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'
# 	# Force an app rerun after switching the sidebar state.
# 	st.rerun()


# if st.button('click me'):
# 	do_somthing()
#
# st.button('click me', on_click=do_somthing)


# First, we will need the following imports for our application.

# Change page layout to make the dashboard take the whole page.



#
# with st.sidebar:
#     st.title("🗓️ #30DaysOfStreamlit")
#     st.header("Day 27 - Streamlit Elements")
#     st.write("Build a draggable and resizable dashboard with Streamlit Elements.")
#     st.write("---")
#
#     # Define URL for media player.
#     media_url = st.text_input("Media URL", value="https://www.youtube.com/watch?v=vIQQR_yq-8I")
#
# # Initialize default data for code editor and chart.
# #
# # For this tutorial, we will need data for a Nivo Bump chart.
# # You can get random data there, in tab 'data': https://nivo.rocks/bump/
# #
# # As you will see below, this session state item will be updated when our
# # code editor change, and it will be read by Nivo Bump chart to draw the data.
#
# if "data" not in st.session_state:
#     st.session_state.data = Path("assets/streamlitdemodata.json").read_text()
#
# # Define a default dashboard layout.
# # Dashboard grid has 12 columns by default.
# #
# # For more information on available parameters:
# # https://github.com/react-grid-layout/react-grid-layout#grid-item-props
#
# layout = [
#     # Editor item is positioned in coordinates x=0 and y=0, and takes 6/12 columns and has a height of 3.
#     dashboard.Item("editor", 0, 0, 6, 3),
#     # Chart item is positioned in coordinates x=6 and y=0, and takes 6/12 columns and has a height of 3.
#     dashboard.Item("chart", 6, 0, 6, 3),
#     # Media item is positioned in coordinates x=0 and y=3, and takes 6/12 columns and has a height of 4.
#     dashboard.Item("media", 0, 2, 12, 4),
# ]
#
# # Create a frame to display elements.
#
# with elements("demo"):
#
#     # Create a new dashboard with the layout specified above.
#     #
#     # draggableHandle is a CSS query selector to define the draggable part of each dashboard item.
#     # Here, elements with a 'draggable' class name will be draggable.
#     #
#     # For more information on available parameters for dashboard grid:
#     # https://github.com/react-grid-layout/react-grid-layout#grid-layout-props
#     # https://github.com/react-grid-layout/react-grid-layout#responsive-grid-layout-props
#
#     with dashboard.Grid(layout, draggableHandle=".draggable"):
#
#         # First card, the code editor.
#         #
#         # We use the 'key' parameter to identify the correct dashboard item.
#         #
#         # To make card's content automatically fill the height available, we will use CSS flexbox.
#         # sx is a parameter available with every Material UI widget to define CSS attributes.
#         #
#         # For more information regarding Card, flexbox and sx:
#         # https://mui.com/components/cards/
#         # https://mui.com/system/flexbox/
#         # https://mui.com/system/the-sx-prop/
#
#         with mui.Card(key="editor", sx={"display": "flex", "flexDirection": "column"}):
#
#             # To make this header draggable, we just need to set its classname to 'draggable',
#             # as defined above in dashboard.Grid's draggableHandle.
#
#             mui.CardHeader(title="Editor", className="draggable")
#
#             # We want to make card's content take all the height available by setting flex CSS value to 1.
#             # We also want card's content to shrink when the card is shrinked by setting minHeight to 0.
#
#             with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
#
#                 # Here is our Monaco code editor.
#                 #
#                 # First, we set the default value to st.session_state.data that we initialized above.
#                 # Second, we define the language to use, JSON here.
#                 #
#                 # Then, we want to retrieve changes made to editor's content.
#                 # By checking Monaco documentation, there is an onChange property that takes a function.
#                 # This function is called everytime a change is made, and the updated content value is passed in
#                 # the first parameter (cf. onChange: https://github.com/suren-atoyan/monaco-react#props)
#                 #
#                 # Streamlit Elements provide a special sync() function. This function creates a callback that will
#                 # automatically forward its parameters to Streamlit's session state items.
#                 #
#                 # Examples
#                 # --------
#                 # Create a callback that forwards its first parameter to a session state item called "data":
#                 # >>> editor.Monaco(onChange=sync("data"))
#                 # >>> print(st.session_state.data)
#                 #
#                 # Create a callback that forwards its second parameter to a session state item called "ev":
#                 # >>> editor.Monaco(onChange=sync(None, "ev"))
#                 # >>> print(st.session_state.ev)
#                 #
#                 # Create a callback that forwards both of its parameters to session state:
#                 # >>> editor.Monaco(onChange=sync("data", "ev"))
#                 # >>> print(st.session_state.data)
#                 # >>> print(st.session_state.ev)
#                 #
#                 # Now, there is an issue: onChange is called everytime a change is made, which means everytime
#                 # you type a single character, your entire Streamlit app will rerun.
#                 #
#                 # To avoid this issue, you can tell Streamlit Elements to wait for another event to occur
#                 # (like a button click) to send the updated data, by wrapping your callback with lazy().
#                 #
#                 # For more information on available parameters for Monaco:
#                 # https://github.com/suren-atoyan/monaco-react
#                 # https://microsoft.github.io/monaco-editor/api/interfaces/monaco.editor.IStandaloneEditorConstructionOptions.html
#
#                 editor.Monaco(
#                     defaultValue=st.session_state.data,
#                     language="json",
#                     onChange=lazy(sync("data"))
#                 )
#
#             with mui.CardActions:
#
#                 # Monaco editor has a lazy callback bound to onChange, which means that even if you change
#                 # Monaco's content, Streamlit won't be notified directly, thus won't reload everytime.
#                 # So we need another non-lazy event to trigger an update.
#                 #
#                 # The solution is to create a button that fires a callback on click.
#                 # Our callback doesn't need to do anything in particular. You can either create an empty
#                 # Python function, or use sync() with no argument.
#                 #
#                 # Now, everytime you will click that button, onClick callback will be fired, but every other
#                 # lazy callbacks that changed in the meantime will also be called.
#
#                 mui.Button("Apply changes", onClick=sync())
#
#         # Second card, the Nivo Bump chart.
#         # We will use the same flexbox configuration as the first card to auto adjust the content height.
#
#         with mui.Card(key="chart", sx={"display": "flex", "flexDirection": "column"}):
#
#             # To make this header draggable, we just need to set its classname to 'draggable',
#             # as defined above in dashboard.Grid's draggableHandle.
#
#             mui.CardHeader(title="Chart", className="draggable")
#
#             # Like above, we want to make our content grow and shrink as the user resizes the card,
#             # by setting flex to 1 and minHeight to 0.
#
#             with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
#
#                 # This is where we will draw our Bump chart.
#                 #
#                 # For this exercise, we can just adapt Nivo's example and make it work with Streamlit Elements.
#                 # Nivo's example is available in the 'code' tab there: https://nivo.rocks/bump/
#                 #
#                 # Data takes a dictionary as parameter, so we need to convert our JSON data from a string to
#                 # a Python dictionary first, with `json.loads()`.
#                 #
#                 # For more information regarding other available Nivo charts:
#                 # https://nivo.rocks/
#
#                 nivo.Bump(
#                     data=json.loads(st.session_state.data),
#                     colors={ "scheme": "spectral" },
#                     lineWidth=3,
#                     activeLineWidth=6,
#                     inactiveLineWidth=3,
#                     inactiveOpacity=0.15,
#                     pointSize=10,
#                     activePointSize=16,
#                     inactivePointSize=0,
#                     pointColor={ "theme": "background" },
#                     pointBorderWidth=3,
#                     activePointBorderWidth=3,
#                     pointBorderColor={ "from": "serie.color" },
#                     axisTop={
#                         "tickSize": 5,
#                         "tickPadding": 5,
#                         "tickRotation": 0,
#                         "legend": "",
#                         "legendPosition": "middle",
#                         "legendOffset": -36
#                     },
#                     axisBottom={
#                         "tickSize": 5,
#                         "tickPadding": 5,
#                         "tickRotation": 0,
#                         "legend": "",
#                         "legendPosition": "middle",
#                         "legendOffset": 32
#                     },
#                     axisLeft={
#                         "tickSize": 5,
#                         "tickPadding": 5,
#                         "tickRotation": 0,
#                         "legend": "ranking",
#                         "legendPosition": "middle",
#                         "legendOffset": -40
#                     },
#                     margin={ "top": 40, "right": 100, "bottom": 40, "left": 60 },
#                     axisRight=None,
#                 )
#
#         # Third element of the dashboard, the Media player.
#
#         with mui.Card(key="media", sx={"display": "flex", "flexDirection": "column"}):
#             mui.CardHeader(title="Media Player", className="draggable")
#             with mui.CardContent(sx={"flex": 1, "minHeight": 0}):
#
#                 # This element is powered by ReactPlayer, it supports many more players other
#                 # than YouTube. You can check it out there: https://github.com/cookpete/react-player#props
#
#                 media.Player(url=media_url, width="100%", height="100%", controls=True)
#
#
#
# # # Taking user input
# # user_input = st.text_input("Enter some text")
# #
# # # Displaying the output
# # st.write(f'You entered: {user_input}')
# #
# # # Slider widget
# # slider = st.slider('Choose a value', min_value=0, max_value=100, value=25)
# #
# # if slider > 50:
# # 	st.write(f'You selected a value greater than 50: {cfg.pull("hello")}')
# #
# # # Display the slider value
# # st.write(f'You selected {slider} as the value')