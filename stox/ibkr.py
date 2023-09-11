from .imports import *
from ib_insync import *
from . import misc

from . import misc, yahoo
from .general import Quantity, TRBC_Codes, Downloader, load_symbol_table
from collections import namedtuple
from omnibelt import unspecified_argument, load_yaml, save_yaml
import omnifig as fig
import omniply as op
from omniply import tool, ToolKit, Context, AbstractGig



@fig.component('ib-extractor')
class IB_Extractor(fig.Configurable):
	def __init__(self, using_notebook=False, host='127.0.0.1', port=4001, client_id=1):
		if using_notebook:
			util.startLoop()
		self.ib = IB()
		self.ib.connect(host, port, clientId=client_id)
		self.host = host
		self.port = port
		self.client_id = client_id

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

	def refresh(self):
		if not self.ib.isConnected():
			self.ib.connect(self.host, self.port, clientId=self.client_id)

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
					  name=True, info=True, industries=True, summary=True, price=True, market_cap=True):
	if isinstance(contract, str):
		contract = ibe.find_contract(contract)
	if snapshot is None and (name or industries or summary or price):
		raw = ibe.snapshot(contract)
		try:
			snapshot = xmltodict.parse(raw)
		except Exception as e:
			snapshot = None

	if name and snapshot is not None:
		company_name = snapshot['ReportSnapshot']['CoIDs']['CoID'][1]['#text']
		print(company_name)

	contract_info = [contract.symbol, contract.currency, contract.primaryExchange, contract.exchange, contract.conId]
	if info:
		if len(contract.description):
			contract_info.append(contract.description)
		print(' | '.join(map(str,contract_info)))
		print()

	if price and snapshot is not None:
		price = snapshot['ReportSnapshot']['Ratios']['Group'][0]['Ratio'][0]['#text']
		price = float(price)
		currency = snapshot['ReportSnapshot']['Ratios']['@PriceCurrency']
		print(f'Price: {price:.2f} {currency}')

	if market_cap and snapshot is not None:
		market_cap = snapshot['ReportSnapshot']['Ratios']['Group'][1]['Ratio'][0]['#text']
		market_cap = float(market_cap) * 1e6
		currency = snapshot['ReportSnapshot']['Ratios']['@PriceCurrency']
		print(f'Market Cap: {Quantity(market_cap, currency)}')

	if industries and snapshot is not None:
		inds = [ind for ind in snapshot['ReportSnapshot']['peerInfo']['IndustryInfo']['Industry']
				if ind['@type'] == 'TRBC']
		if len(inds) > 0:
			industry = inds[0]['#text']
			trbc = TRBC_Codes()
			sector = trbc.get_sector(inds[0]['@code'])
			print(f'{sector}  ::  {industry}')
			print()

	if summary and snapshot is not None:
		summary_text = snapshot['ReportSnapshot']['TextInfo']['Text'][0]['#text']
		if len(summary_text) > 300:
			summary_text = summary_text[:300] + '...'
		print(summary_text)

	return snapshot




def save_symbol_table(table):
	root = misc.assets_root()
	path = root / 'symbol-table.yml'
	if path.exists():
		save_yaml(load_symbol_table(), root / 'symbol-table_backup.yml')
	save_yaml(table, path)
	return path



def add_symbol_row(table, yfsym, contract, force=False, extra=None):
	if yfsym in table:
		if force:
			print(f'Overwriting {yfsym!r} {table["ibkr-contract"][yfsym]}')
		else:
			raise ValueError(f'{yfsym} already in table: {table["ibkr-contract"][yfsym]}')

	ibsym = contract.symbol
	ibrows = {v['ibkr-contract']['symbol']: v for k, v in table.items()}
	if ibsym in ibrows:
		if force:
			print(f'Overwriting {ibsym!r} {ibrows[ibsym]}')
		else:
			raise ValueError(f'{ibsym} already in table: {ibrows[ibsym]}')

	row = {
		'symbol': contract.symbol,
		'currency': contract.currency,
		'primaryExchange': contract.primaryExchange,
		'conId': contract.conId,
		'exchange': contract.exchange,
	}
	if contract.description is not None:
		row['description'] = contract.description
	if extra is None:
		extra = {}
	table.setdefault(yfsym, {}).update({"ibkr-contract": row, **extra})
	print(f'Added {yfsym!r} {row}')


@fig.component('downloader/ibkr')
class IBKR_Downloader(Downloader, fig.Configurable):
	def __init__(self, ibe=None, *, keys=None, date=None, root=None, connect=False, **kwargs):
		if root is None:
			root = misc.ibkr_root()
		super().__init__(root=root, **kwargs)
		if keys is None:
			keys = self._report_keys
		self.ibe = ibe
		if connect:
			self.refresh_api()
		self.default_keys = keys
		self.date = date
		self.symbol_table = load_symbol_table()

	_report_keys = ['snapshot', 'ownership', 'finances', 'statements', 'recommendations']
	def report_keys(self):
		yield from self._report_keys

	def report_path(self, ticker, key, date=unspecified_argument):
		if date is unspecified_argument:
			date = self.date
		ct = self.as_contract(ticker)
		path = misc.get_date_path(self.root, str(ct.conId), date=date)
		return path / f'{key}.xml'

	def as_contract(self, ct):
		info = ct
		if isinstance(info, str):
			info = self.symbol_table[info].get('ibkr-contract')
		assert info is not None, f'No contract for {ct}'
		if not isinstance(info, Contract):
			info = Stock(**info)
		return info

	def load_report(self, ticker, key, date=unspecified_argument):
		path = self.report_path(ticker, key, date=date)
		with open(path, 'r') as f:
			return xmltodict.parse(f.read())

	def refresh_api(self):
		if self.ibe is None or not self.ibe.ib.isConnected():
			self.ibe = IB_Extractor()

	def download_reports(self, ticker, *, keys=None, ignore_existing=False, pbar=None, date=unspecified_argument):
		if keys is None:
			keys = self.default_keys

		results = {}

		ct = self.as_contract(ticker)

		itr = keys if pbar is None else pbar(keys, total=len(keys))
		for key in itr:
			if pbar is not None:
				itr.set_description(f'{ticker} {key}')

			filepath = self.report_path(ct, key, date=date)
			if filepath.exists() and not ignore_existing:
				continue

			self.refresh_api()

			try:
				data = getattr(self.ibe, key)(ct)
				if data is None:
					data = ''
				with open(filepath, 'w') as f:
					f.write(data)
			except KeyboardInterrupt:
				raise
			except Exception as e:
				results[key] = e
			else:
				results[key] = filepath
		return results



# def report_path(ct, root=None, date='last', ):
# 	path = misc.get_date_path(root, str(cid), date=date)
#
#
# def download_reports(info, root=None, date=None, ibe=None, pbar=None, keys=None):
# 	if ibe is None:
# 		ibe = IB_Extractor()
# 	elif not ibe.ib.isConnected():
# 		ibe = IB_Extractor()
#
# 	if root is None:
# 		root = misc.ibkr_root()
#
# 	if not isinstance(info, Contract):
# 		info = Stock(**info)
# 	ct = info
# 	cid = ct.conId
#
# 	report_fns = {
# 		'snapshot': ibe.snapshot,
# 		'ownership': ibe.ownership,
# 		'finances': ibe.finances,
# 		'statements': ibe.statements,
# 		'recommendations': ibe.recommendations,
# 		# 'calendar': ibe.calendar,
# 	}
# 	if keys is not None:
# 		report_fns = {k: v for k, v in report_fns.items() if k in keys}
#
# 	itr = report_fns.items()
# 	if pbar is not None:
# 		itr = pbar(itr, total=len(report_fns))
#
# 	results = {}
# 	for name, fn in itr:
# 		if pbar is not None:
# 			itr.set_description(f'{name}')
# 		filepath = path / f'{name}.xml'
# 		if filepath.exists():
# 			continue
# 		try:
# 			data = fn(ct)
# 			if data is None:
# 				continue
# 			with open(filepath, 'w') as f:
# 				f.write(data)
# 		except KeyboardInterrupt:
# 			raise
# 		except Exception as e:
# 			results[name] = e
# 		else:
# 			results[name] = path
#
# 	return path
#
#
# def old_load_stock_data(row, date='last', root=None, keys=None, *, skip_missing=True):
# 	if root is None:
# 		root = misc.ibkr_root()
#
# 	cid = row['conId']
# 	path = misc.get_date_path(root, str(cid), date=date)
#
# 	if not path.exists():
# 		raise ValueError(f'No data for {cid} on {date}')
#
# 	if keys is None:
# 		keys = report_keys
#
# 	data = {}
#
# 	missing = []
#
# 	for key in keys:
# 		filepath = path / f'{key}.xml'
# 		if not filepath.exists():
# 			missing.append(key)
# 			continue
#
# 		with open(filepath) as f:
# 			data.update(xmltodict.parse(f.read()))
#
# 	if len(missing):
# 		if skip_missing:
# 			print(f'Missing {missing} for {cid} on {date}')
# 		else:
# 			raise ValueError(f'Missing {missing} for {cid} on {date}')
#
# 	return data


@fig.component('ibkr-loader')
class IBKR_Loader(ToolKit, fig.Configurable):
	def __init__(self, downloader=None, **kwargs):
		if downloader is None:
			downloader = IBKR_Downloader()
		super().__init__(**kwargs)
		self.downloader = downloader
		self.extend(tool(report)(lambda contract, date: self.downloader.load_report(contract, report, date=date))
					 for report in self.downloader.report_keys())

	@tool('contract')
	def get_contract(self, ticker):
		return self.downloader.as_contract(ticker)

	@tool('conId')
	def get_conId(self, contract):
		return contract.conId

	@tool('primaryExchange')
	def get_primaryExchange(self, contract):
		return contract.primaryExchange

	@tool('ibsym')
	def get_ibsym(self, contract):
		return contract.symbol


	# @tool('ckpt_path')
	# def get_ckpt_path(self, conId, date='last'):
	# 	path = misc.get_date_path(self.root, str(conId), date)
	# 	return path
	#
	# def _load_xml(self, path):
	# 	with open(path, 'r') as f:
	# 		return xmltodict.parse(f.read())
	#
	# @tool('snapshot')
	# def load_snapshot(self, ckpt_path):
	# 	path = ckpt_path / 'snapshot.xml'
	# 	if not path.exists():
	# 		raise op.GadgetFailure(f'No snapshot for {ckpt_path}')
	# 	return self._load_xml(path)['ReportSnapshot']
	#
	# @tool('ownership')
	# def load_ownership(self, ckpt_path):
	# 	path = ckpt_path / 'ownership.xml'
	# 	if not path.exists():
	# 		raise op.GadgetFailure(f'No ownership for {ckpt_path}')
	# 	return self._load_xml(path)
	#
	# @tool('finances')
	# def load_finances(self, ckpt_path):
	# 	path = ckpt_path / 'finances.xml'
	# 	if not path.exists():
	# 		raise op.GadgetFailure(f'No finances for {ckpt_path}')
	# 	return self._load_xml(path)
	#
	# @tool('statements')
	# def load_statements(self, ckpt_path):
	# 	path = ckpt_path / 'statements.xml'
	# 	if not path.exists():
	# 		raise op.GadgetFailure(f'No statements for {ckpt_path}')
	# 	return self._load_xml(path)
	#
	# @tool('recommendations')
	# def load_recommendations(self, ckpt_path):
	# 	path = ckpt_path / 'recommendations.xml'
	# 	if not path.exists():
	# 		raise op.GadgetFailure(f'No recommendations for {ckpt_path}')
	# 	return self._load_xml(path)['REarnEstCons']



@fig.component('ibkr-stats')
class IBKR_Stats(ToolKit, fig.Configurable):
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
		vals = snapshot['Issues']['Issue']
		val = vals[0] if isinstance(vals, list) else vals
		return val['Exchange']['@Code']

	@tool('exchange')
	def get_exchange_from_rec(self, recommendations):
		return recommendations['Company']['SecurityInfo']['Security']['Exchange']['@code']

	@tool('exchange_name')
	def get_exchange_name(self, snapshot):
		vals = snapshot['Issues']['Issue']
		val = vals[0] if isinstance(vals, list) else vals
		return val['Exchange']['#text']

	@tool('country')
	def get_country_code_from_snapshot(self, snapshot):
		vals = snapshot['Issues']['Issue']
		val = vals[0] if isinstance(vals, list) else vals
		return val['Exchange']['@Country']

	@tool('country')
	def get_country_code_from_rec(self, recommendations):
		loc = recommendations['Company']['SecurityInfo']['Security']['SecIds']['SecId'][0]
		assert loc['@type'] == 'ISIN', f'Expected ISIN in {loc}'
		return loc['#text']

	@tool('isin')
	def get_isin_from_snapshot(self, snapshot):
		vals = snapshot['Issues']['Issue']
		val = vals[0] if isinstance(vals, list) else vals
		val = val['IssueID'][2]
		assert val['@Type'] == 'ISIN', f'Expected ISIN in {val}'
		return val['#text']

	@tool('isin')
	def get_isin_from_rec(self, recommendations):
		options = recommendations['Company']['SecurityInfo']['Security']['SecIds']['SecId']['#text']
		for o in options:
			if o['@type'] == 'ISIN':
				return o['#text']
		raise op.GadgetFailure(f'Expected ISIN in {options}')

	@tool('price')
	def get_price(self, recommendations):
		stats = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem']
		if stats[0]['@type'] != 'CLPRICE':
			raise op.GadgetFailure('No price')
		entry = stats[0]
		assert entry['@unit'] == 'U' and entry['@type'] == 'CLPRICE', f'Expected CLPRICE in {entry}'
		return Quantity(float(entry['#text']), entry['@currCode'])

	@tool('market_cap')
	def get_market_cap(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][1]
		assert entry['@unit'] == 'M' and entry['@type'] == 'MARKETCAP', f'Expected MARKETCAP in {entry}'
		return Quantity(float(entry['#text']) * 1e6, entry['@currCode'])

	@tool('high_52w')
	def get_high_52w(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][2]
		assert entry['@unit'] == 'U' and entry['@type'] == '52WKHIGH', f'Expected 52WKHIGH in {entry}'
		return Quantity(float(entry['#text']), entry['@currCode'])

	@tool('low_52w')
	def get_low_52w(self, recommendations):
		entry = recommendations['Company']['SecurityInfo']['Security']['MarketData']['MarketDataItem'][3]
		assert entry['@unit'] == 'U' and entry['@type'] == '52WKLOW', f'Expected 52WKLOW in {entry}'
		return Quantity(float(entry['#text']), entry['@currCode'])

	# @tool('industry_trbc')
	# def get_industry_trbc(self, recommendations):
	# 	return recommendations['Company']['CompanyInfo']['Sector']['#text']

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
		if isinstance(val, dict):
			val = val['#text']
		return ' '.join(v.capitalize() for v in val.split(' '))

	# skipped address and phone and contact person info and email
	@tool('website')
	def get_website(self, snapshot):
		val = snapshot['webLinks']['webSite']
		return val['#text']

	@tool('industry')
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



@fig.component('ibkr-derived')
class IBKR_Derived(ToolKit, fig.Configurable):
	def __init__(self, *, trbc=None, **kwargs):
		if trbc is None:
			trbc = TRBC_Codes()
		super().__init__(**kwargs)
		self.trbc = trbc


	@tool('sector')
	def get_sector(self, industry_trbc_code):
		return self.trbc.get_sector(industry_trbc_code)




