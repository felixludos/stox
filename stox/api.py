from .imports import *
from ib_insync import *


class IB_Extractor:
	def __init__(self, using_notebook=False, host='127.0.0.1', port=4001, client_id=1):
		if using_notebook:
			util.startLoop()
		self.ib = IB()
		self.ib.connect(host, port, clientId=client_id)

	def find_all_contracts(self, symbol, sec_type='STK', currency='', exchange=''):
		contract = Contract()
		contract.symbol = symbol
		contract.secType = sec_type
		contract.currency = currency
		contract.exchange = exchange

		out = self.ib.reqContractDetails(contract)
		return [c.contract for c in out]

	def find_contract(self, symbol, sec_type='STK', currency='', exchange=''):
		contracts = self.find_all_contracts(symbol, sec_type, currency, exchange)
		return contracts[0]

	def as_contract(self, info):
		if isinstance(info, Contract):
			return info
		return self.find_contract(info)

	def snapshot(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'ReportSnapshot')

	def ownership(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'ReportsOwnership')

	def finances(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'ReportsFinSummary')

	def statements(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'ReportsFinStatements')

	def recommendations(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'RESC')

	def calendar(self, info):
		contract = self.as_contract(info)
		return self.ib.reqFundamentalData(contract, 'CalendarReport')

	def search(self, query: str):
		return [r.contract for r in self.ib.reqMatchingSymbols(query)]






















