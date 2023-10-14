from pathlib import Path
import json, random
import pandas as pd
from omnibelt import load_yaml, save_yaml, load_json, save_json
import streamlit as st
from stox import misc
from stox import load_symbol_table
from stox.general import DistributionLoader
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
	return infos
world = load_world()
syms = {info['ticker']: info for info in world}
max_weight = max(10., min(float(int(420 / len(world))//10*10), 100.))

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

@st.cache_resource
def load_features():
	features = cfg.pull('features', [])
	formatters = {}
	if isinstance(features, dict):
		formatters = features
		features = list(features.keys())
	formatters = cfg.pull('formatters', formatters)
	# if 'weight' not in formatters:
	# 	formatters['weight'] = lit.WeightFormatter()
	return features, formatters
features, formatters = load_features()

@st.cache_resource
def init_data_table():
	cols = ['sel', 'weight', 'ticker', *features]
	rows = []
	for info in world:
		row = {}
		for k in features:
			if k == 'sel':
				val = False
			elif k == 'weight':
				val = pf.get(info['ticker'], 0)
			else:
				try:
					val = info[k]
				except:
					print(f'Failed to get {k} for {info["ticker"]}')
					val = None
	# 		row[k] = val
	# 	rows.append(row)
	# df = pd.DataFrame(rows, columns=cols)
	# return df
	pass
initial_table = init_data_table()

def viz_world():
	default_formatter = lit.DefaultFormatter()
	cols = ['sel', 'weight', 'ticker', *features]
	rows = [{k: formatters.get(k, default_formatter).format_value(k, info[k]) for k in cols} for info in world]
	df = pd.DataFrame(rows, columns=cols)
	return df

df = viz_world()
col_config = {col: formatter.column_config(col) for col, formatter in formatters.items()}

if 'weight' not in col_config:
	col_config['weight'] = st.column_config.ProgressColumn(
			"Weight",
			help="The weight of the stock in the portfolio",
			format="%.2g%%",
			min_value=0,
			max_value=max_weight,
		)

edited_df = st.data_editor(df, column_config={k:v for k,v in col_config.items() if v is not None})

if st.button('Update'):
	for tk, sel, wt in zip(edited_df['ticker'], edited_df['sel'], edited_df['weight']):
		syms[tk]['sel'] = sel
	st.rerun()

st.write(f'Selected: {", ".join([info["ticker"] for info in world if info["sel"]])}')

# p.display()





