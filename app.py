from pathlib import Path
import json, random
import pandas as pd
from omnibelt import load_yaml, save_yaml, load_json, save_json
import streamlit as st
import plotly.express as px
from stox import misc
from stox import load_symbol_table
from stox.general import DistributionLoader, Quantity, PctChange
from stox import streamlit as lit
import omnifig as fig


if 'sidebar_state' not in st.session_state:
	st.session_state.sidebar_state = 'expanded'
st.set_page_config(layout="wide", initial_sidebar_state=st.session_state.sidebar_state)

@st.cache_resource
def load_config():
	fig.initialize()
	return fig.create_config('app')
cfg = load_config()
lit.World.cfg = cfg

# def load_data_file(path: Path):
# 	if path.suffix == '.csv':
# 		return pd.read_csv(path)
# 	elif path.suffix == '.json':
# 		return pd.read_json(path)
# 	elif path.suffix == '.yaml':
# 		data = load_yaml(path)
# 		return pd.DataFrame(data)
# 	return None


@st.cache_resource#(allow_output_mutation=True)
def get_world():
	return [lit.World.create()]
manager = get_world()
world = manager[0]
syms = {info['ticker']: info for info in world}

dat = lit.DisplayData(world)

def viz_world():
	cols = ['sel', 'weight', 'ticker', *world.features]
	rows = [{k: info[k] for k in cols}
			for info in sorted(world, key=lambda info: info['order']) if not info['hidden']]
	df = pd.DataFrame(rows, columns=cols)
	return df
df = viz_world()

col_config = {
	'weight': st.column_config.ProgressColumn(
		"Weight",
		help="The weight of the stock in the portfolio",
		format="%.2g%%",
		min_value=0,
		max_value=dat.max_weight,
		),
	'recommendation_mean': st.column_config.NumberColumn('Rec'),

}

col1, col2, _ = st.columns([1, 1, 5])
with col1:
	st.button('Actualize')

edited_df = st.data_editor(df, column_config={key: cc for key, cc in col_config.items()
											  if key in df.columns})

with col2:
	if st.button('Update'):
		for tk, sel, wt in zip(edited_df['ticker'], edited_df['sel'], edited_df['weight']):
			syms[tk]['sel'] = sel
		st.rerun()


# st.write(f'Selected: {", ".join([info["ticker"] for info in world if info["sel"]])}')

st.write(f'Total: {sum(info["weight"] for info in world):.2f}')


new_path = dat.display()


col1, col2 = st.columns(2)

pie_settings = dict(
	autosize=False,
	width=500,
	height=500,
	margin=dict(
		l=50,
		r=50,
		b=100,
		t=100,
		pad=2,
	),
	# paper_bgcolor="LightSteelBlue",
)

with col1:
	fig = px.pie(df, values='weight', names='sector', title='Sector',
				 # hover_data=['weight'],
				 labels={'weight':'Portfolio Weight'})

	fig.update_layout(**pie_settings)
	st.plotly_chart(fig)

with col2:
	fig = px.pie(df, values='weight', names='country', title='Country',
				 # hover_data=['weight'],
				 labels={'weight': 'Portfolio Weight'})
	fig.update_layout(**pie_settings)
	st.plotly_chart(fig)


if new_path is not None:
	print(f'Replacing world with {new_path}')
	manager[0] = lit.World.create(new_path)
	st.rerun()

