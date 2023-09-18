from . import misc
import requests
from omnibelt import unspecified_argument, save_json, load_json
import omnifig as fig
from omniply import tool, ToolKit, Context, AbstractGig

from .general import Downloader, Quantity


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
				if isinstance(data, dict) and 'Note' in data:
					raise ValueError(f'API call failed: {data["Note"]}')
				save_json(data, filepath)
			except KeyboardInterrupt:
				raise
			except Exception as e:
				results[key] = e
			else:
				results[key] = filepath
		return results



class ReportLoader:
	def __init__(self, downloader, report):
		if downloader is None:
			downloader = Alpha_Vantage_Downloader()
		self.downloader = downloader
		self.report = report

	def __call__(self, ticker, date=unspecified_argument):
		return self.downloader.load_report(ticker, self.report, date=date)



@fig.component('loader/alpha-vantage')
class Alpha_Vantage_Loader(ToolKit, fig.Configurable):
	def __init__(self, downloader=None, **kwargs):
		if downloader is None:
			downloader = Alpha_Vantage_Downloader()
		super().__init__(**kwargs)
		self.downloader = downloader
		self.extend(tool(report)(ReportLoader(downloader, report)) for report in self.downloader.report_keys())


@fig.component('stats/alpha-vantage')
class Alpha_Vantage_Stats(ToolKit, fig.Configurable):
	@tool('sector')
	def get_sector(self, overview):
		return overview.get('Sector', '').capitalize()

	@tool('industry')
	def get_industry(self, overview):
		return overview.get('Industry', '').capitalize()

	@tool('market_cap')
	def get_market_cap(self, overview):
		return Quantity(float(overview.get('MarketCapitalization')), overview.get('Currency'))

	@tool('peg_ratio')
	def get_peg_ratio(self, overview):
		return float(overview.get('PEGRatio', float('nan')))

	@tool('pe_ratio')
	def get_pe_ratio(self, overview):
		return float(overview.get('PERatio', float('nan')))

	@tool('dividend_yield')
	def get_dividend_yield(self, overview):
		return Quantity(float(overview.get('DividendYield', float('nan')))*100, '%')

	@tool('eps')
	def get_eps(self, overview):
		return Quantity(float(overview.get('EPS', float('nan'))), overview.get('Currency'))

	@tool('beta')
	def get_beta(self, overview):
		return float(overview.get('Beta', float('nan')))

	@tool('profit_margin')
	def get_profit_margin(self, overview):
		return Quantity(float(overview.get('ProfitMargin', float('nan')))*100, '%')

	@tool('target_price')
	def get_target_price(self, overview):
		return Quantity(float(overview.get('AnalystTargetPrice', float('nan'))), overview.get('Currency'))

	@tool('trailing_pe')
	def get_trailing_pe(self, overview):
		return float(overview.get('TrailingPE', float('nan')))

	@tool('forward_pe')
	def get_forward_pe(self, overview):
		return float(overview.get('ForwardPE', float('nan')))

	@tool('high_52w')
	def get_high_52w(self, overview):
		return Quantity(float(overview.get('52WeekHigh', float('nan'))), overview.get('Currency'))

	@tool('low_52w')
	def get_low_52w(self, overview):
		return Quantity(float(overview.get('52WeekLow', float('nan'))), overview.get('Currency'))

	@tool('av_50d')
	def get_av_50d(self, overview):
		return Quantity(float(overview.get('50DayMovingAverage', float('nan'))), overview.get('Currency'))

	@tool('av_200d')
	def get_av_200d(self, overview):
		return Quantity(float(overview.get('200DayMovingAverage', float('nan'))), overview.get('Currency'))

	@tool('ebitda')
	def get_ebitda(self, overview):
		return Quantity(float(overview.get('EBITDA', float('nan'))), overview.get('Currency'))

	@tool('description')
	def get_description(self, overview):
		return overview.get('Description', '')

	@tool('company_name')
	def get_name(self, overview):
		return overview.get('Name', '')



