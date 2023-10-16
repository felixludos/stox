from pathlib import Path
import json, random
import pandas as pd
from omnibelt import load_yaml, save_yaml, load_json, save_json
import streamlit as st
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
def load_world():
	tickers = cfg.pull('tickers', [], silent=True)
	cfg.print(f'Found {len(tickers)} tickers.')
	infos = [load_ticker(yfsym) for yfsym in tickers]
	infos = infos[:5]
	return infos
world = load_world()
syms = {info['ticker']: info for info in world}

_dis_root = misc.assets_root() / 'dis'
def load_data_file(path: Path):
	if path.suffix == '.csv':
		return pd.read_csv(path)
	elif path.suffix == '.json':
		return pd.read_json(path)
	elif path.suffix == '.yaml':
		data = load_yaml(path)
		return pd.DataFrame(data)
	return None
def load_portfolio(name):
	path = _dis_root / f'{name}.json'
	raw = load_json(path) if path.exists() else {}
	print(f'Loaded portfolio {name} with {len(raw)} symbols.')
	data = {k: v for k, v in raw.items() if k in syms}
	print(f'Found {len(data)} symbols in the current universe.')
	total = sum(data.values())
	data = {k: 100. * v / total for k, v in data.items() if v > 0}
	return data
@st.cache_resource
def prepare_active_portfolio():
	name = cfg.pull('portfolio', 'default')
	pf = load_portfolio(name)
	for info in world:
		info['sel'] = False
		info['weight'] = pf.get(info['ticker'], 0)
	return pf
pf = prepare_active_portfolio()

features = [
	'price',
	'yield',
	'peg_ratio',
	'shares',
	'beta',
	'log_market_cap',
	'recommendation_mean',
	'overall_risk',
	'ibsym',
]

# @st.cache_resource
# def get_display_state():
dat = lit.DisplayData()
dat.populate(world, features)

@st.cache_resource
def init_data_table():
	cols = ['sel', 'weight', 'ticker', *features]
	for info in world:
		for col in cols:
			val = info[col]

			if isinstance(val, (Quantity, PctChange)):
				info[col] = val.amount

		info['locked'] = False

	return []
initial_table = init_data_table()

def viz_world():
	default_formatter = lit.DefaultFormatter()
	cols = ['sel', 'weight', 'ticker', *features]
	rows = [{k: default_formatter(k, info[k], info=info) for k in cols} for info in world]
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
}
edited_df = st.data_editor(df, column_config={key: cc for key, cc in col_config.items()
											  if key in df.columns})

if st.button('Update'):
	for tk, sel, wt in zip(edited_df['ticker'], edited_df['sel'], edited_df['weight']):
		syms[tk]['sel'] = sel
	st.rerun()

st.write(f'Selected: {", ".join([info["ticker"] for info in world if info["sel"]])}')


dat.display()

# p.display()





