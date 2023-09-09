
import sys, os
from pathlib import Path
import json
import time

import numpy as np
import pandas as pd

import yfinance as yf

from .general import Quantity, PctChange, Downloader
from . import misc

from omnibelt import unspecified_argument

_DEFAULT_ROOT = Path(__file__).parents[1]

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
			return data.to_csv(cls.fmt_path(root, key), index=True)
			return data.to_json(cls.fmt_path(root, key), date_format='iso', date_unit='s')
		except ValueError:
			return data.to_json(cls.fmt_path(root, key), orient='split', date_format='iso', date_unit='s')
	
	
	@classmethod
	def load(cls, root, key):
		try:
			return pd.read_csv(cls.fmt_path(root, key), index_col=0)
			return pd.read_json(cls.fmt_path(root, key), date_unit='s')
		except ValueError:
			return pd.read_json(cls.fmt_path(root, key), orient='split', date_unit='s')




class Yahoo_Downloader(Downloader):
	_default_datatypes = {
		# 'ticker': JsonLoader,
		'isin': JsonLoader,
		'info': JsonLoader,
		'history': PandasLoader,
		'calendar': PandasLoader, # TODO: update when yfinance is updated

		'recommendations': PandasLoader, # TODO: update when yfinance is updated
		'sustainability': PandasLoader, # TODO: update when yfinance is updated

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

	def __init__(self, root=None, date=None, **kwargs):
		if root is None:
			root = misc.yahoo_root()
		super().__init__(root=root, **kwargs)
		self.date = date

	def report_keys(self):
		yield from self._default_datatypes.keys()

	def report_path(self, ticker, key, date=unspecified_argument):
		if date is unspecified_argument:
			date = self.date
		path = misc.get_date_path(self.root, ticker, date=date)
		root = _get_path_info(ticker, root=self.root, date=date)
		path = self._default_datatypes[key].fmt_path(root, key)



def _get_path_root(dirname='yahoo_data', root=None):
	if root is None:
		root = _DEFAULT_ROOT / dirname
	os.makedirs(str(root), exist_ok=True)
	return root

def _get_path_info(ticker, root=None, dirname='yahoo_data', date='last'):
	root = _get_path_root(dirname=dirname, root=root)
	return misc.get_date_path(root, ticker, date=date)

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
			 keys=None, pbar=None):
	path = _get_path_info(ticker, root=root, date=date, dirname=dirname)
	
	tk = yf.Ticker(ticker)
	
	if keys is None:
		keys = _default_datatypes
	if history_kwargs is None:
		history_kwargs = {'period': 'max'}
	
	itr = keys.items()
	if pbar is not None:
		itr = pbar(itr, total=len(keys))

	fails = {}

	# try:
	for key, store in itr:
		if pbar is not None:
			itr.set_description(f'{ticker}: {key}')
		if store.fmt_path(path, key).exists():
			continue
		try:
			data = tk.history(**history_kwargs) if key == 'history' else getattr(tk, key)
			# if data is not None:
			store.save(data, path, key)
		except KeyboardInterrupt:
			raise
		except Exception as e:
			fails[key] = e
			# print(ticker, key, data)
			# raise
	# except KeyError:
	# 	if skip_failures:
	# 		return None
	# 	raise

	return fails


def load(ticker, date='last', root=None, dirname='yahoo_data', ticker_type=None):
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


from omniply import ToolKit, tool



class Yahoo_Loader(ToolKit):
	def __init__(self, root=None):
		super().__init__()
		if root is None:
			root = misc.yahoo_root()
		self.root = root

	@tool('ckpt_path')
	def get_ckpt_path(self, ticker, date='last'):
		path = misc.get_date_path(self.root, ticker, date)
		return path

	@tool('info')
	def get_info(self, ckpt_path):
		return JsonLoader.load(ckpt_path, 'info')

	@tool('splits')
	def get_splits(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'splits')

	@tool('dividends')
	def get_dividends(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'dividends')

	@tool('history')
	def get_history(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'history')

	@tool('isin')
	def get_isin(self, ckpt_path):
		return JsonLoader.load(ckpt_path, 'isin')

	@tool('balancesheet')
	def get_balancesheet(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'balancesheet')

	@tool('cashflow')
	def get_cashflow(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'cashflow')

	@tool('financials')
	def get_financials(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'financials')

	@tool('quarterly_balancesheet')
	def get_quarterly_balancesheet(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'quarterly_balancesheet')

	@tool('quarterly_cashflow')
	def get_quarterly_cashflow(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'quarterly_cashflow')

	@tool('quarterly_financials')
	def get_quarterly_financials(self, ckpt_path):
		return PandasLoader.load(ckpt_path, 'quarterly_financials')



class Yahoo_Info(ToolKit):
	def __init__(self, root=None):
		super().__init__()
		if root is None:
			root = misc.yahoo_root()
		self.root = root

	@tool('country')
	def get_country(self, info):
		return info.get('country')

	@tool('city')
	def get_city(self, info):
		return info.get('city')

	@tool('website')
	def get_website(self, info):
		return info.get('website')

	@tool('sector')
	def get_sector(self, info):
		return info.get('sector')

	@tool('industry')
	def get_industry(self, info):
		return info.get('industry')

	@tool('business_summary')
	def get_business_summary(self, info):
		return info.get('longBusinessSummary')

	@tool('employees')
	def get_employees(self, info):
		return info.get('fullTimeEmployees')

	@tool('audit_risk')
	def get_audit_risk(self, info):
		return info.get('auditRisk')

	@tool('board_risk')
	def get_board_risk(self, info):
		return info.get('boardRisk')

	@tool('compensation_risk')
	def get_compensation_risk(self, info):
		return info.get('compensationRisk')

	@tool('share_holder_risk')
	def get_share_holder_risk(self, info):
		return info.get('shareHolderRightsRisk')

	@tool('overall_risk')
	def get_overall_risk(self, info):
		return info.get('overallRisk')

	@tool('high_52w')
	def get_high_52w(self, info):
		return Quantity(info.get('fiftyTwoWeekHigh'), info.get('currency'))

	@tool('low_52w')
	def get_low_52w(self, info):
		return Quantity(info.get('fiftyTwoWeekLow'), info.get('currency'))

	@tool('cash_per_share')
	def get_cash_per_share(self, info):
		return Quantity(info.get('totalCashPerShare'), info.get('currency'))

	@tool('debt_to_equity')
	def get_debt_to_equity(self, info):
		return info.get('debtToEquity')

	@tool('earnings_growth')
	def get_earnings_growth(self, info):
		return Quantity(info.get('earningsGrowth', float('nan'))*100, info.get('currency'))

	@tool('yield')
	def get_yield(self, info):
		return Quantity(info.get('dividendYield', 0.)*100, '%')
		# return Quantity(info.get('yield', float('nan')), info.get('currency'))

	@tool('revenue')
	def get_revenue(self, info):
		return Quantity(info.get('totalRevenue'), info.get('currency'))

	@tool('gross_profit')
	def get_gross_profit(self, info):
		return Quantity(info.get('grossProfits'), info.get('currency'))

	@tool('free_cash_flow')
	def get_free_cash_flow(self, info):
		return Quantity(info.get('freeCashflow'), info.get('currency'))

	@tool('operating_cash_flow')
	def get_operating_cash_flow(self, info):
		return Quantity(info.get('operatingCashflow'), info.get('currency'))

	@tool('operating_income')
	def get_operating_income(self, info):
		return Quantity(info.get('operatingIncome'), info.get('currency'))

	@tool('ebitda')
	def get_ebitda(self, info):
		return Quantity(info.get('ebitda'), info.get('currency'))

	@tool('debt')
	def get_debt(self, info):
		return Quantity(info.get('totalDebt'), info.get('currency'))

	@tool('cash')
	def get_cash(self, info):
		return Quantity(info.get('totalCash'), info.get('currency'))

	@tool('current_ratio')
	def get_current_ratio(self, info):
		return info.get('currentRatio')

	@tool('quick_ratio')
	def get_quick_ratio(self, info):
		return info.get('quickRatio')

	@tool('beta')
	def get_beta(self, info):
		return info.get('beta')

	@tool('trailing_pe') # past 12 months price / earnings
	def get_trailing_pe(self, info):
		return info.get('trailingPE')

	@tool('forward_pe') # projected future price / earnings
	def get_forward_pe(self, info):
		return info.get('forwardPE')

	@tool('volume')
	def get_volume(self, info):
		return info.get('volume')

	@tool('volume_10d')
	def get_volume_10d(self, info):
		return info.get('averageVolume10days')

	@tool('market_cap')
	def get_market_cap(self, info):
		return Quantity(info.get('marketCap'), info.get('currency'))

	@tool('peg_ratio')
	def get_peg_ratio(self, info):
		return info.get('pegRatio')

	@tool('price_to_book')
	def get_price_to_book(self, info):
		return info.get('priceToBook')

	@tool('trailing_eps') # past 12 months earnings per share
	def get_trailing_eps(self, info):
		return info.get('trailingEps')

	@tool('forward_eps') # projected future earnings per share
	def get_forward_eps(self, info):
		return info.get('forwardEps')

	@tool('exchange')
	def get_exchange(self, info):
		return info.get('exchange')

	@tool('company_short_name')
	def get_short_name(self, info):
		return info.get('shortName')

	@tool('company_name')
	def get_long_name(self, info):
		return info.get('longName')

	@tool('price')
	def get_price(self, info):
		return Quantity(info.get('currentPrice'), info.get('currency'))

	@tool('recommendation_mean')
	def get_recommendation_mean(self, info):
		return info.get('recommendationMean')

	@tool('recommendation_key')
	def get_recommendation_key(self, info):
		return info.get('recommendationKey')

	@tool('number_of_analysts')
	def get_number_of_analysts(self, info):
		return info.get('numberOfAnalystOpinions')

	@tool('target_mean_price')
	def get_target_mean_price(self, info):
		return Quantity(info.get('targetMeanPrice'), info.get('currency'))

	@tool('target_high_price')
	def get_target_high_price(self, info):
		return Quantity(info.get('targetHighPrice'), info.get('currency'))

	@tool('target_low_price')
	def get_target_low_price(self, info):
		return Quantity(info.get('targetLowPrice'), info.get('currency'))

	@tool('target_median_price')
	def get_target_median_price(self, info):
		return Quantity(info.get('targetMedianPrice'), info.get('currency'))

	@tool('change_52w')
	def get_change_52w(self, info):
		return PctChange(info.get('52WeekChange', float('nan')) * 100)

	@tool('held_percent_institutions')
	def get_held_percent_institutions(self, info):
		return Quantity(info.get('heldPercentInstitutions', float('nan'))*100, '%')

	@tool('held_percent_insiders')
	def get_held_percent_insiders(self, info):
		return Quantity(info.get('heldPercentInsiders', float('nan'))*100, '%')

	@tool('profit_margins')
	def get_profit_margins(self, info):
		return Quantity(info.get('profitMargins', float('nan'))*100, '%')


	@tool('target_mean_change')
	def target_mean_change(self, price: Quantity, target_mean_price: Quantity):
		assert price.unit == target_mean_price.unit, f'{price} vs {target_mean_price}'
		change = target_mean_price.amount / price.amount - 1
		return PctChange(100 * change)

	@tool('target_high_change')
	def target_high_change(self, price: Quantity, target_high_price: Quantity):
		assert price.unit == target_high_price.unit, f'{price} vs {target_high_price}'
		change = target_high_price.amount / price.amount - 1
		return PctChange(100 * change)

	@tool('target_low_change')
	def target_low_change(self, price: Quantity, target_low_price: Quantity):
		assert price.unit == target_low_price.unit, f'{price} vs {target_low_price}'
		change = target_low_price.amount / price.amount - 1
		return PctChange(100 * change)

	@tool('target_median_change')
	def target_median_change(self, price: Quantity, target_median_price: Quantity):
		assert price.unit == target_median_price.unit, f'{price} vs {target_median_price}'
		change = target_median_price.amount / price.amount - 1
		return PctChange(100 * change)

	@tool('perf52w')
	def compute_performance_52w(self, price, high_52w, low_52w):
		assert price.unit == high_52w.unit == low_52w.unit, f'{price} vs {high_52w} vs {low_52w}'
		return (price.amount - low_52w.amount) / (high_52w.amount - low_52w.amount)



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

