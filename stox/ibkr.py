from .imports import *
from ib_insync import *
from . import misc

from dataclasses import dataclass
from . import misc, yahoo
from collections import namedtuple
import omniply as op
from omniply import tool, ToolKit, Context




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


report_keys = ['snapshot', 'ownership', 'finances', 'statements', 'recommendations']


def download_reports(ibe, info, root=None, date=None, pbar=None, keys=None):
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
	if keys is not None:
		report_fns = {k: v for k, v in report_fns.items() if k in keys}

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


def old_load_stock_data(row, date='last', root=None, keys=None, *, skip_missing=True):
	if root is None:
		root = misc.ibkr_root()

	cid = row['conId']
	path = misc.get_date_path(root / str(cid), date=date)

	if not path.exists():
		raise ValueError(f'No data for {cid} on {date}')

	if keys is None:
		keys = report_keys

	data = {}

	missing = []

	for key in keys:
		filepath = path / f'{key}.xml'
		if not filepath.exists():
			missing.append(key)
			continue

		with open(filepath) as f:
			data.update(xmltodict.parse(f.read()))

	if len(missing):
		if skip_missing:
			print(f'Missing {missing} for {cid} on {date}')
		else:
			raise ValueError(f'Missing {missing} for {cid} on {date}')

	return data



@dataclass
class Money:
	amount: float
	currency: str

	def __str__(self):
		return f'{self.amount:.2f} {self.currency}'

	def __repr__(self):
		return f'{self.amount:.2f} {self.currency}'


class IBKR_Loader(ToolKit):
	def __init__(self, date='last', root=None):
		super().__init__()
		if root is None:
			root = misc.ibkr_root()
		self.root = root
		self.date = date

	@tool('ckpt_date')
	def get_ckpt_date(self, conId):
		path = misc.get_date_path(self.root / str(conId), self.date)
		return path.name

	@tool('ckpt_path')
	def get_ckpt_path(self, conId, ckpt_date):
		return misc.get_date_path(self.root / str(conId), ckpt_date)

	def _load_xml(self, path):
		with open(path, 'r') as f:
			return xmltodict.parse(f.read())

	@tool('snapshot')
	def load_snapshot(self, ckpt_path):
		path = ckpt_path / 'snapshot.xml'
		if not path.exists():
			raise op.GadgetFailure(f'No snapshot for {ckpt_path}')
		return self._load_xml(path)['ReportSnapshot']

	@tool('ownership')
	def load_ownership(self, ckpt_path):
		path = ckpt_path / 'ownership.xml'
		if not path.exists():
			raise op.GadgetFailure(f'No ownership for {ckpt_path}')
		return self._load_xml(path)

	@tool('finances')
	def load_finances(self, ckpt_path):
		path = ckpt_path / 'finances.xml'
		if not path.exists():
			raise op.GadgetFailure(f'No finances for {ckpt_path}')
		return self._load_xml(path)

	@tool('statements')
	def load_statements(self, ckpt_path):
		path = ckpt_path / 'statements.xml'
		if not path.exists():
			raise op.GadgetFailure(f'No statements for {ckpt_path}')
		return self._load_xml(path)

	@tool('recommendations')
	def load_recommendations(self, ckpt_path):
		path = ckpt_path / 'recommendations.xml'
		if not path.exists():
			raise op.GadgetFailure(f'No recommendations for {ckpt_path}')
		return self._load_xml(path)['REarnEstCons']


class IBKR_Stats(ToolKit):
	@tool('company_name')
	def get_company_name_from_snapshot(self, snapshot):
		val = snapshot['CoIDs']['CoID'][1]
		assert val['@Type'] == 'CompanyName', f'Expected CompanyName in {val}'
		return val['#text']

	@tool('company_name')
	def get_company_name_from_rec(self, recommendations):
		return recommendations['Company']['CoName']['Name']['#text']

	@tool('exchange')
	def get_exchange_from_snapshot(self, snapshot):
		val = snapshot['Issues']['Issue']['Exchange']
		return val['@Code']

	@tool('exchange')
	def get_exchange_from_rec(self, recommendations):
		return recommendations['Company']['SecurityInfo']['Security']['Exchange']['@code']

	@tool('exchange_name')
	def get_exchange_name(self, snapshot):
		val = snapshot['Issues']['Issue']['Exchange']
		return val['#text']

	@tool('country')
	def get_country_code_from_snapshot(self, snapshot):
		val = snapshot['Issues']['Issue']['Exchange']
		return val['@Country']

	@tool('country')
	def get_country_code_from_rec(self, recommendations):
		loc = recommendations['Company']['SecurityInfo']['Security']['SecIds']['SecId'][0]
		assert loc['@type'] == 'ISIN', f'Expected ISIN in {loc}'
		return loc['#text']

	@tool('isin')
	def get_isin_from_snapshot(self, snapshot):
		val = snapshot['Issues']['Issue']['IssueID'][2]
		assert val['@Type'] == 'ISIN', f'Expected ISIN in {val}'
		return val['#text']

	@tool('isin')
	def get_isin_from_rec(self, recommendations):
		options = recommendations['Company']['SecurityInfo']['Security']['SecIds']['SecId']['#text']
		for o in options:
			if o['@type'] == 'ISIN':
				return o['#text']
		raise op.GadgetError(f'Expected ISIN in {options}')

	@tool('clprice')
	def get_clprice(self, recommendations):
		return recommendations['Company']['SecurityInfo']['Security']['@clprice']

	@tool('price')
	def get_price(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][0]
		assert entry['@unit'] == 'U' and entry['@type'] == 'CLPRICE', f'Expected CLPRICE in {entry}'
		return Money(float(entry['#text']), entry['@currCode'])

	@tool('market_cap')
	def get_market_cap(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][1]
		assert entry['@unit'] == 'M' and entry['@type'] == 'MARKETCAP', f'Expected MARKETCAP in {entry}'
		return Money(float(entry['#text']) * 1e6, entry['@currCode'])

	@tool('high_52w')
	def get_high_52w(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][2]
		assert entry['@unit'] == 'U' and entry['@type'] == '52WKHIGH', f'Expected 52WKHIGH in {entry}'
		return Money(float(entry['#text']), entry['@currCode'])

	@tool('low_52w')
	def get_low_52w(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][3]
		assert entry['@unit'] == 'U' and entry['@type'] == '52WKLOW', f'Expected 52WKLOW in {entry}'
		return Money(float(entry['#text']), entry['@currCode'])

	@tool('sector')
	def get_sector(self, recommendations):
		return recommendations['Company']['CompanyInfo']['Sector']['#text']

	@tool('employees')
	def get_employees(self, snapshot):
		val = snapshot['CoGeneralInfo']['Employees']
		return int(val['#text'])

	@tool('employees_date')
	def get_employees_date(self, snapshot):
		val = snapshot['CoGeneralInfo']['Employees']
		return val['@LastUpdated']

	@tool('business_summary')
	def get_company_summary(self, snapshot):
		val = snapshot['TextInfo']['Text'][0]
		assert val['@Type'] == 'Business Summary', f'Expected Business Summary in {val}'
		return val['#text']

	@tool('brief')
	def get_brief(self, snapshot):
		val = snapshot['TextInfo']['Text'][1]
		assert val['@Type'] == 'Financial Summary', f'Expected Financial Summary in {val}'
		return val['#text']

	@tool('brief_date')
	def get_brief_date(self, snapshot):
		val = snapshot['TextInfo']['Text'][1]
		assert val['@Type'] == 'Financial Summary', f'Expected Financial Summary in {val}'
		return val['@LastModified']

	@tool('country_code')
	def get_country(self, snapshot):
		val = snapshot['contactInfo']['country']
		return val['@code']

	@tool('country_name')
	def get_country_name(self, snapshot):
		val = snapshot['contactInfo']['country']
		return val['#text']

	@tool('city')
	def get_city(self, snapshot):
		val = snapshot['contactInfo']['city']
		return val['#text']

	# skipped address and phone and contact person info and email
	@tool('website')
	def get_website(self, snapshot):
		val = snapshot['webLinks']['webSite']
		return val['#text']

	@tool('industry_trbc')
	def get_industry_trbc(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'TRBC']
		assert len(vals) == 1, f'Expected 1 TRBC in {vals}'
		return vals[0]['#text']

	@tool('industry_trbc_code')
	def get_industry_trbc_code(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'TRBC']
		assert len(vals) == 1, f'Expected 1 TRBC in {vals}'
		return vals[0]['@code']

	@tool('industry')
	@tool('industry_naics')
	def get_industry_naics(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'NAICS']
		assert len(vals), f'Expected NAICS in {vals}'
		return [v['#text'] for v in vals]

	@tool('industry_naics_code')
	def get_industry_naics_code(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'NAICS']
		assert len(vals), f'Expected NAICS in {vals}'
		return [v['@code'] for v in vals]

	@tool('industry_sic')
	def get_industry_sic(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'SIC']
		assert len(vals), f'Expected SIC in {vals}'
		return [v['#text'] for v in vals]

	@tool('industry_sic_code')
	def get_industry_sic_code(self, snapshot):
		full = snapshot['peerInfo']['IndustryInfo']['Industry']
		vals = [row for row in full if row['@type'] == 'SIC']
		assert len(vals), f'Expected SIC in {vals}'
		return [v['@code'] for v in vals]






