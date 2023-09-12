from . import misc
import requests
from omnibelt import unspecified_argument, save_json, load_json
import omnifig as fig
from omniply import tool, ToolKit, Context, AbstractGig

from .general import Downloader


class _AlphaVantageBase:
	_query_url_template = 'https://www.alphavantage.co/query?{query}'

	def __init__(self, API_KEY=None):
		if API_KEY is None:
			API_KEY = misc.get_secret('ALPHA_VANTAGE_API_KEY')
		self._api_key = API_KEY


	def _send_call(self, **params):
		if 'apikey' not in params:
			params['apikey'] = self._api_key
		query = '&'.join(f'{key}={value}' for key, value in params.items())

		url = self._query_url_template.format(query=query)
		response = requests.get(url)
		data = response.json()
		return data



class AlphaVantageStocks(_AlphaVantageBase):
	def overview(self, symbol: str):
		return self._send_call(function='OVERVIEW', symbol=symbol)

	def income_statement(self, symbol: str):
		return self._send_call(function='INCOME_STATEMENT', symbol=symbol)

	def balance_sheet(self, symbol: str):
		return self._send_call(function='BALANCE_SHEET', symbol=symbol)

	def cash_flow(self, symbol: str):
		return self._send_call(function='CASH_FLOW', symbol=symbol)

	def earnings(self, symbol: str):
		return self._send_call(function='EARNINGS', symbol=symbol)

	def earnings_calendar(self, symbol: str):
		return self._send_call(function='EARNINGS_CALENDAR', symbol=symbol)

	def ipo_calendar(self, symbol: str):
		return self._send_call(function='IPO_CALENDAR', symbol=symbol)

	def listing_status(self, symbol: str):
		return self._send_call(function='LISTING_STATUS', symbol=symbol)


# add economic indicators, forex, etc.

@fig.component('downloader/alpha-vantage')
class Alpha_Vantage_Downloader(Downloader, fig.Configurable):
	def __init__(self, av_api=None, *, root=None, keys=None, date=None, **kwargs):
		if av_api is None:
			av_api = AlphaVantageStocks()
		if root is None:
			root = misc.alpha_vantage_root()
		super().__init__(root=root, **kwargs)
		if keys is None:
			keys = list(self.report_keys())
		self.av = av_api
		self.default_keys = keys
		self.date = date

	_report_keys = ['overview', 'income_statement', 'balance_sheet', 'cash_flow', 'earnings',
					'earnings_calendar', 'ipo_calendar', 'listing_status']
	def report_keys(self):
		yield from self._report_keys

	def report_path(self, ticker, key, date=unspecified_argument):
		if date is unspecified_argument:
			date = self.date
		path = misc.get_date_path(self.root, ticker, date=date)
		return path / f'{key}.json'

	def load_report(self, ticker, key, date=unspecified_argument):
		path = self.report_path(ticker, key, date=date)
		return load_json(path)
		# with path.open('r') as f:
		# 	return xmltodict.parse(f.read())

	def download_reports(self, ticker, *, keys=None, ignore_existing=False, pbar=None, date=unspecified_argument):
		if keys is None:
			keys = self.default_keys

		results = {}

		itr = keys if pbar is None else pbar(keys, total=len(keys))
		for key in itr:
			if pbar is not None:
				itr.set_description(f'{ticker} {key}')

			filepath = self.report_path(ticker, key, date=date)
			if filepath.exists() and not ignore_existing:
				continue

			try:
				data = getattr(self.av, key)(ticker)
				if data is None:
					data = ''
				save_json(data, filepath)
			except KeyboardInterrupt:
				raise
			except Exception as e:
				results[key] = e
			else:
				results[key] = filepath
		return results


@fig.component('loader/alpha-vantage')
class Alpha_Vantage_Loader(ToolKit, fig.Configurable):
	def __init__(self, downloader=None, **kwargs):
		if downloader is None:
			downloader = Alpha_Vantage_Downloader()
		super().__init__(**kwargs)
		self.downloader = downloader
		self.extend(tool(report)(lambda ticker, date: self.downloader.load_report(ticker, report, date=date))
					for report in self.downloader.report_keys())




