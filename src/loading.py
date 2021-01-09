
import sys, os
from pathlib import Path
from omnibelt import load_json, save_json

from .fidelity import load_etf_pie, load_etf_analyst, load_etf_holdings, load_etf_snapshot, \
	load_stock_contained, load_stock_history, load_stock_snapshot

SITES = {
	'EQUITY': ['snapshot', 'news', 'history', 'analyst', 'basket'],
	'ETF': ['snapshot', 'composition', 'analyst', 'holdings'],
}

EXTRACTORS = {
	'ETF': {
		'snapshot': load_etf_snapshot,
		'holdings': load_etf_holdings,
		'composition': load_etf_pie,
		'analyst': load_etf_analyst,
		
	},
	'EQUITY': {
		'snapshot': load_stock_snapshot,
		'basket': load_stock_contained,
		'history': load_stock_history,
	},
}

IDENTS = {
	'ETF': {
		'snapshot': 'snapshot*',
		'holdings': 'etfholdings*',
		'analyst': 'analyst*',
		'composition': 'portfolio*',
		
	},
	'EQUITY': {
		'analyst': 'analyst*',
		'history': 'history/*',
		'news': 'basic*',
		'snapshot': 'snapshot*',
	},
}


_loaded = {}

def clear_loaded():
	_loaded.clear()

def load(cat, group, root=None, force=False, pbar=None):
	
	if (cat, group) in _loaded:
		return _loaded[cat,group]
	
	if root is None:
		root = Path('raw/dates')
		dates = list(root.glob('*'))
		root = sorted(dates)[-1]
	else:
		root = Path(root)
	
	savepath = root / f'{cat}-{group}.json'
	
	if savepath.is_file() and not force:
		data = load_json(savepath)
	else:
		dataroot = root /  cat.lower()
		paths = list(dataroot.glob(f'{IDENTS[cat][group]}'))
		paths = pbar(paths) if pbar is not None else paths
		data = dict( EXTRACTORS[cat][group](path) for path in paths)
	
		save_json(data, savepath)
	
	_loaded[cat, group] = data
	
	return data

def _deep_get(src, key, *remainder):
	try:
		val = src[key]
	except:
		# print(src, key)
		val = None
		
	if len(remainder):
		return _deep_get(val, *remainder)
	return val

def collect(full, features, data=None):
	
	if data is None:
		data = {}
		
	for tk, raw in full.items():
		if tk not in data:
			data[tk] = {}
		
		info = data[tk]
		for title, src in features.items():
			if title not in info:
				if not isinstance(src, tuple):
					src = (src,)
				val = _deep_get(raw, *src)
				if isinstance(val, dict):
					info.update(val)
				else:
					info[title] = val
	
	return data





