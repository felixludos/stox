from .imports import *
from ib_insync import *
from . import misc


class IB_Extractor:
	def __init__(self, using_notebook=False, host='127.0.0.1', port=4001, client_id=1):
		if using_notebook:
			util.startLoop()
		self.ib = IB()
		self.ib.connect(host, port, clientId=client_id)

	def find_all_contracts(self, symbol, secType='STK', currency='', primaryExchange=''):
		contract = Contract()
		contract.symbol = symbol
		contract.secType = secType
		contract.currency = currency
		contract.primaryExchange = primaryExchange

		out = self.ib.reqContractDetails(contract)
		return [c.contract for c in out]

	def find_contract(self, symbol, secType='STK', currency='', primaryExchange=''):
		contracts = self.find_all_contracts(symbol, secType, currency, primaryExchange)
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


def describe_contract(ibe: IB_Extractor, contract: str | Contract, *, snapshot=None,
					  name=True, info=True, industries=True, summary=True, price=True):
	if isinstance(contract, str):
		contract = ibe.find_contract(contract)
	if snapshot is None and (name or industries or summary or price):
		snapshot = xmltodict.parse(ibe.snapshot(contract))

	if name:
		company_name = snapshot['ReportSnapshot']['CoIDs']['CoID'][1]['#text']
		print(company_name)

	contract_info = [contract.symbol, contract.currency, contract.primaryExchange, contract.conId]
	if info:
		if len(contract.description):
			contract_info.append(contract.description)
		print(' | '.join(map(str,contract_info)))
		print()

	if price:
		price = snapshot['ReportSnapshot']['Ratios']['Group'][0]['Ratio'][0]['#text']
		price = float(price)
		currency = snapshot['ReportSnapshot']['Ratios']['@PriceCurrency']
		print(f'Price: {price:.2f} {currency}')

	if industries:
		industry_list = [e['#text'] for e in snapshot['ReportSnapshot']['peerInfo']['IndustryInfo']['Industry']]
		print('\n'.join(industry_list))
		print()

	if summary:
		summary_text = snapshot['ReportSnapshot']['TextInfo']['Text'][0]['#text']
		if len(summary_text) > 300:
			summary_text = summary_text[:300] + '...'
		print(summary_text)

	return snapshot


def load_symbol_table():
	root = misc.assets_root()
	path = root / 'yahoo2ibkr.yml'
	data = load_yaml(path)
	return data



def save_symbol_table(table):
	root = misc.assets_root()
	path = root / 'yahoo2ibkr.yml'
	if path.exists():
		save_yaml(load_symbol_table(), root / 'yahoo2ibkr_backup.yml')
	save_yaml(table, path)
	return path



def add_symbol_row(table, yfsym, contract, force=False):
	if yfsym in table:
		if force:
			print(f'Overwriting {yfsym!r} {table[yfsym]}')
		else:
			raise ValueError(f'{yfsym} already in table: {table[yfsym]}')

	ibsym = contract.symbol
	ibrows = {v['symbol']: v for k, v in table.items()}
	if ibsym in ibrows:
		if force:
			print(f'Overwriting {ibsym!r} {ibrows[ibsym]}')
		else:
			raise ValueError(f'{ibsym} already in table: {ibrows[ibsym]}')

	row = {
		'symbol': contract.symbol,
		'currency': contract.currency,
		'primaryExchange': contract.primaryExchange,
		'conID': contract.conId,
		'exchange': contract.exchange,
	}
	table[yfsym] = row
	print(f'Added {yfsym!r} {row}')



def download_reports(ibe, info, root=None, date=None, pbar=None):
	if root is None:
		root = misc.ibkr_root()

	cid = info['conId']
	path = misc.get_date_path(root / str(cid), date=date)

	ct = Stock(**info)
	report_fns = {
		'snapshot': ibe.snapshot,
		'ownership': ibe.ownership,
		'finances': ibe.finances,
		'statements': ibe.statements,
		'recommendations': ibe.recommendations,
		# 'calendar': ibe.calendar,
	}

	itr = report_fns.items()
	if pbar is not None:
		itr = pbar(itr, total=len(report_fns))

	for name, fn in itr:
		if pbar is not None:
			itr.set_description(f'{name}')
		filepath = path / f'{name}.xml'
		if filepath.exists():
			continue
		data = fn(ct)
		if data is None:
			continue
		with open(filepath, 'w') as f:
			f.write(data)

	return path














