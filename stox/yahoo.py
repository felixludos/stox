
import sys, os
from pathlib import Path
import json

from datetime import datetime
import time

import numpy as np
import pandas as pd

import yfinance as yf

# from omnibelt import get_now

STD_FMT = "%y%m%d"

_DEFAULT_ROOT = Path(__file__).parents[1]

def get_date(fmt=None):
	if fmt is None:
		fmt = STD_FMT
	return datetime.now().strftime(fmt)


class JsonLoader:
	@staticmethod
	def fmt_path(root, key):
		return root / f'{key}.json'
	
	@classmethod
	def save(cls, data, root, key):
		return json.dump(data, cls.fmt_path(root, key).open('w'))
	
	@classmethod
	def load(cls, root, key):
		return json.load(cls.fmt_path(root, key).open('r'))



class PandasLoader(JsonLoader):
	@classmethod
	def save(cls, data, root, key):
		try:
			if not isinstance(data, (pd.DataFrame, pd.Series)):
				return super().save(data, root, key)
			return data.to_json(cls.fmt_path(root, key))
		except ValueError:
			return data.to_json(cls.fmt_path(root, key), orient='split')
	
	
	@classmethod
	def load(cls, root, key):
		try:
			return pd.read_json(cls.fmt_path(root, key))
		except ValueError:
			return pd.read_json(cls.fmt_path(root, key), orient='split')



_default_datatypes = {
	# 'ticker': JsonLoader,
	'isin': JsonLoader,
	'info': JsonLoader,
	'history': PandasLoader,
	'calendar': PandasLoader,
	
	'recommendations': PandasLoader,
	'sustainability': PandasLoader,
	
	'dividends': PandasLoader,
	'splits': PandasLoader,
	
	'institutional_holders': PandasLoader,
	'major_holders': PandasLoader,
	'mutualfund_holders': PandasLoader,
	
	'balancesheet': PandasLoader,
	'cashflow': PandasLoader,
	'earnings': PandasLoader,
	'financials': PandasLoader,
	
	'quarterly_balancesheet': PandasLoader,
	'quarterly_cashflow': PandasLoader,
	'quarterly_earnings': PandasLoader,
	'quarterly_financials': PandasLoader,
	
	
}

def _get_path_root(dirname='yahoo_data', root=None):
	if root is None:
		root = _DEFAULT_ROOT / dirname
	os.makedirs(str(root), exist_ok=True)
	return root

def _get_path_info(ticker, root=None, dirname='yahoo_data', date='last'):
	root = _get_path_root(dirname=dirname, root=root)
	path = root / ticker
	path.mkdir(exist_ok=True)
	
	if date == 'last':
		options = sorted(path.glob('*'), key=lambda p: p.name)#[-1]
		if len(options):
			date = options[-1]
		else:
			date = None
	if date is None:
		date = get_date()
	path = path / date
	path.mkdir(exist_ok=True)
	return path

def load_portfolio(name, root=None, dirname='portfolios',
				   datadir='yahoo_data', date='last', download_self=False):
	pathroot = _get_path_root(dirname=dirname, root=root)
	
	path = JsonLoader.fmt_path(pathroot, name)
	if not path.exists():
		return
	pf = JsonLoader.load(pathroot, name)
	if download_self:
		pf['self'] = download(name, root=root, dirname=dirname)
	return pf


def save_portfolio(name, data, root=None, dirname='portfolios',):
	pathroot = _get_path_root(dirname=dirname, root=root)
	JsonLoader.save(data, pathroot, name)


def download(ticker, date='last', root=None, dirname='yahoo_data',
			 history_kwargs=None, ticker_type=None, skip_failures=False,
			 keys=None, pbar=None, allow_download=True):
	path = _get_path_info(ticker, root=root, date=date, dirname=dirname)
	
	tk = yf.Ticker(ticker)
	
	if keys is None:
		keys = _default_datatypes
	if history_kwargs is None:
		history_kwargs = {'period': 'max'}
	
	itr = keys.items()
	if pbar is not None:
		itr = pbar(itr, total=len(keys))
	
	try:
		for key, store in itr:
			if pbar is not None:
				itr.set_description(f'{ticker}: {key}')
			# print(store.fmt_path(path, key))
			if not store.fmt_path(path, key).exists():
				if not allow_download:
					return None
				data = None
				try:
					data = tk.history(**history_kwargs) if key == 'history' else getattr(tk, key)
					# if data is not None:
					store.save(data, path, key)
				except:
					print(ticker, key, data)
					raise
	except KeyError:
		if skip_failures:
			return None
		raise

	if ticker_type is None:
		ticker_type = OfflineTicker
	return ticker_type(ticker, date=date, root=root)



class OfflineTicker:
	def __init__(self, ticker, root=None, date='last', keys=None):
		path = _get_path_info(ticker, root=root, date=date)
		self._path = path
		self.ticker = ticker
		if keys is None:
			keys = _default_datatypes
		self._load_keys = keys
	
	def __str__(self):
		return f'<{self.ticker}>'
	
	def __repr__(self):
		return f'<{self.ticker}>'
	
	def __getattr__(self, item):
		try:
			return self.__getattribute__(item)
		except AttributeError:
			if item not in self._load_keys:
				raise
			path = self._load_keys[item].fmt_path(self._path, item)
			if path.exists():
				obj = self._load_keys[item].load(self._path, item)
			else:
				obj = None
			setattr(self, item, obj)
			return obj



# def load(ticker, root=None, date=None, keys=None, ticker_type=None, **kwargs):
# 	path = _get_path_info(ticker, root=root, date=date)
# 	if not path.exists():
# 		return download(ticker, root=root, date=date, keys=keys,
# 		                ticker_type=ticker_type, **kwargs)
# 	if ticker_type is None:
# 		ticker_type = OfflineTicker
# 	return ticker_type(ticker, date=date, root=root)

from PIL import Image
from io import BytesIO
import requests
import textwrap

def wrap(s, w):
	return textwrap.fill(s, w)

def profile_item(tk, width=100):
	item = tk.info
	
	target = item.get('targetMeanPrice', 0.)
	if target is None:
		target = 0.
	
	profile = '''{symbol} - {shortName}

Sector: {sector}
Industry: {industry}

Location: {city}, {country}

Recommendation: {recommendationMean:1.1f} ({target:1.1f}%)
PEG: {peg:1.1f}
Beta: {beta:1.1f}
MarketCap (log): {marketCap}
Yield: {yieldpercent:1.1f}%

{longName}

{summary}
Website: {website}

Quote: {quote}'''.format(symbol=item.get('symbol'), shortName=item.get('shortName'),
                         sector=item.get('sector'), industry=item.get('industry'),
                         city=item.get('city'), country=item.get('country'),
                         longName=item.get('longName'), website=item.get('website'),
		close=item.get('previousClose', 0.),
	quote='https://finance.yahoo.com/quote/' + item.get('symbol'),
				# percentage=100 * item.get('ratio', 0.),
			   yieldpercent=0. if item.get('dividendYield') is None else item.get('dividendYield') * 100,
			   summary = wrap(item.get('longBusinessSummary', ''),width),
			             recommendationMean=item.get('recommendationMean',-1.) if item.get('recommendationMean',-1.) is not None else -1.,
			             target=(target/item.get('previousClose',1.))*100
			                    - (100. if 'targetMeanPrice' in item else 0.),
			             marketCap=np.log10(item.get('marketCap',1.) if item.get('marketCap',1.) is not None else 1.),
                         peg=item.get('pegRatio', float('nan')) if item.get('pegRatio', float('nan')) is not None else float('nan'),
                         beta=item.get('beta', float('nan')) if item.get('beta', float('nan')) is not None else float('nan'),
			   )
	try:
		response = requests.get(item['logo_url'])
		img = Image.open(BytesIO(response.content))
	except:
		img = None
	return profile, img


# def update(ticker):
# 	raise NotImplementedError


