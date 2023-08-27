from . import misc
import requests


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



