from . import misc
import requests


class AlphaVantage:
	_base_url = 'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={apikey}'

	def __init__(self, API_KEY=None):
		if API_KEY is None:
			API_KEY = misc.get_secret('ALPHA_VANTAGE_API_KEY')
		self._api_key = API_KEY


	def _send_call(self, function, symbol):
		url = self._base_url.format(function=function, symbol=symbol, apikey=self._api_key)
		response = requests.get(url)
		data = response.json()
		return data


	def overview(self, symbol: str):
		return self._send_call('OVERVIEW', symbol)

	def income_statement(self, symbol: str):
		return self._send_call('INCOME_STATEMENT', symbol)

	def balance_sheet(self, symbol: str):
		return self._send_call('BALANCE_SHEET', symbol)

	def cash_flow(self, symbol: str):
		return self._send_call('CASH_FLOW', symbol)

	def earnings(self, symbol: str):
		return self._send_call('EARNINGS', symbol)

	def earnings_calendar(self, symbol: str):
		return self._send_call('EARNINGS_CALENDAR', symbol)

	def ipo_calendar(self, symbol: str):
		return self._send_call('IPO_CALENDAR', symbol)

	def listing_status(self, symbol: str):
		return self._send_call('LISTING_STATUS', symbol)






