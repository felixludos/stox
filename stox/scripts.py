from pathlib import Path
from tqdm import tqdm
from unidecode import unidecode
from tabulate import tabulate
import pandas as pd
from . import misc
from .yahoo import Yahoo_Downloader
from .ibkr import (load_symbol_table, IB_Extractor, IBKR_Downloader,
				   add_symbol_row, describe_contract, save_symbol_table)
import omnifig as fig



@fig.script('download')
def download_symbols(config: fig.Configuration):
	config.silent = config.pull('silent', config.silent, silent=True)
	symbol_table = load_symbol_table()
	len(symbol_table)

	date = config.pull('date', misc.get_date())
	date = str(date)

	outpath = config.pull('outpath', 'download-results.yml')

	downloaders = config.pull('downloaders', {})
	assert len(downloaders), 'No downloaders specified'

	tickers = config.pull('tickers', None)
	if tickers is None:
		tickers = list(symbol_table.keys())
	else:
		bad = [tk for tk in tickers if tk not in symbol_table]
		if len(bad):
			if 'ibkr' in downloaders:
				raise ValueError(f'Unknown tickers (for IBKR): {bad}')
			else:
				config.print(f'WARNING unknown tickers (for IBKR): {bad}')
	config.print(f'Downloading {len(tickers)} tickers')

	results = {}
	num_errors = 0
	num_new = 0

	pbar = config.pull('pbar', True)
	itr = tickers
	if pbar:
		itr = tqdm(itr)
	for ticker in itr:
		for name, downloader in downloaders.items():
			if pbar:
				itr.set_description(f'{ticker} :: {name} ({num_new} new; {num_errors} errors)')
			reports = downloader.download_reports(ticker, pbar=None, date=date)
			num_new += sum(not isinstance(v, Exception) for v in reports.values())
			errs = {k: repr(v) for k, v in reports.items() if isinstance(v, Exception)}
			if len(errs):
				num_errors += len(errs)
				results.setdefault(ticker, {})[name] = errs

	failures = [(tk, name, '\n'.join(f'{k} : {v}' for k,v in errs.items()))
				for tk, dls in results.items() for name, errs in dls.items()]
	if len(failures):
		config.print(tabulate(failures, headers=['ticker', 'downloader', 'errors']))
	config.print(f'{num_new} reports successfully downloaded and {num_errors} errors.')

	if outpath is not None:
		misc.save_yaml(results, outpath)
	return results



@fig.script('ib-search')
def find_symbol(config: fig.Configuration):
	config.silent = config.pull('silent', config.silent, silent=True)
	config.push('api._type', 'ib-extractor', silent=True, overwrite=False)
	ibe = config.pull('api')
	ibe.refresh()

	symbol_table = load_symbol_table()
	existing_contracts = {v['ibkr-contract']['conId'] for k, v in symbol_table.items()}

	overwrite = True
	yfsym = config.pulls('yfsym', 'yf', default=None)
	add_symbol = config.pulls('add-symbol', 'add', default=yfsym is not None)
	if add_symbol and yfsym is None:
		raise ValueError('Must provide a yahoo finance symbol to add to table')
	if yfsym is not None and yfsym in symbol_table:
		overwrite = config.pulls('overwrite', 'f', default=False)
		config.print(f'{yfsym} already exists: {symbol_table["ibkr-contract"][yfsym]}')

	secType = config.pull('secType', 'STK')
	primaryExchange = config.pulls('exchange', 'ex', default=None)
	if isinstance(primaryExchange, str):
		primaryExchange = [primaryExchange]
	currency = config.pulls('currency', 'm', default=None)
	if isinstance(currency, str):
		currency = [currency]

	srcs = []

	ibsym = config.pulls('ibsym', 'ib', 'sym', default=None)
	if ibsym is not None:
		contract_info = {}
		if secType is not None:
			contract_info['secType'] = secType
		if currency is not None and len(currency) == 1:
			contract_info['currency'] = currency[0]
		if primaryExchange is not None and len(primaryExchange) == 1:
			contract_info['primaryExchange'] = primaryExchange[0]
		cts = ibe.find_all_contracts(ibsym, **contract_info)
		srcs.append(cts)

	query = config.pulls('query', 'q', default=None)
	if yfsym is not None and ibsym is None and query is None:
		query = yfsym.split('.')[0]
	if query is not None:
		if config.pull('sanitize-query', True):
			query = unidecode(query)
		search_results = [c for c in ibe.search(query) if c.secType == secType]
		srcs.append(search_results)

	auto_select = config.pulls('auto-select', 'auto', default=False)

	assert len(srcs), f'No sources specified (provide at least one of "query" or "ibsym")'

	locs = [set(c.conId for c in src) for src in srcs]
	def score(ct):
		return (sum(ct.conId in loc for loc in locs),
				secType is None or ct.secType == secType,
				currency is None or ct.currency in currency,
				primaryExchange is None or ct.primaryExchange in primaryExchange,
				max(misc.str_similarity(yfsym.lower(), ct.symbol.lower()) if yfsym is not None else 0,
					misc.str_similarity(query.lower(), ct.description.lower()) if query is not None and ct.description is not None else 0,
					misc.str_similarity(query.lower(), ct.symbol.lower()) if query is not None else 0),
				# -ct.conId
				-len(ct.description) if ct.description is not None else 0,
				)

	cts = sorted(set(ct for src in srcs for ct in src), key=score, reverse=True)

	if config.pull('return-all', False):
		return cts

	assert len(cts), 'No contracts found'

	index = config.pull('index', None)

	if index is None:
		config.print('Search Results:')
		config.print(tabulate([(i, c.symbol, c.currency, c.primaryExchange, c.conId, c.description)
						for i, c in reversed(list(enumerate(cts)))],
					   headers=['index', 'symbol', 'currency', 'primaryExchange', 'conId', 'description']))

		if auto_select:
			ct = cts[0]
		else:
			config.print()
			idx = None
			while idx is None:
				raw = input('Select contract by index (default=0): ')
				try:
					idx = int(raw) if len(raw) else 0
				except ValueError:
					config.print(f'Invalid index: {raw!r}')
			ct = cts[idx]

	else:
		ct = cts[index]

	config.print('*' * 80)
	config.print()

	ct = ibe.ib.reqContractDetails(ct)[0].contract
	describe_contract(ibe, ct)
	config.print()

	if add_symbol:
		if overwrite:
			# config.print(f'Adding symbol {yfsym} {ct}')
			add_symbol_row(symbol_table, yfsym, ct, force=True,
						   extra=config.pull('extra', {}, silent=True))
			save_symbol_table(symbol_table)
		else:
			config.print(f'{yfsym} already exists: {symbol_table["ibkr-contract"][yfsym]}')
			config.print('Not overwriting (set "overwrite" to overwrite)')
	else:
		config.print(f'Not saving symbol to table ({"exists" if ct.conId in existing_contracts else "does not exist"})')
	config.print()

	return ct



@fig.script('euro-stats')
def save_stats(config: fig.Configuration):
	config.silent = config.pull('silent', config.silent, silent=True)
	container_source = config.peek('container')
	# ctx = container_source.create()
	# ctx['ticker'] = 'BBVA.MC'
	# ctx['date'] = 'last'
	def create_container(yfsym, date):
		with container_source.silence():
			ctx = container_source.create()
		ctx['ticker'] = yfsym
		ctx['date'] = date
		return ctx

	outpath = config.pull('outpath', str(misc.assets_root()/'euro-stats.csv'))
	outpath = Path(outpath)
	if outpath.exists() and not config.pull('overwrite', False):
		config.print(f'File {outpath} already exists (use "overwrite" to overwrite)')
		return

	symbols_table = load_symbol_table()

	tickers = config.pull('tickers', None)
	if tickers is None:
		tickers = [sym for sym, info in symbols_table.items() if info['ibkr-contract'].get('currency') == 'EUR']

	# portfolio = config.pull('portfolio', None)
	# if portfolio is None:
	# 	portfolio_path = config.pull('portfolio-path', None)
	# 	if portfolio_path is not None:
	# 		portfolio = misc.extract_tickers_and_shares(portfolio_path)
	# 		portfolio = {k: v for k, v in portfolio}

	if any(tk not in symbols_table for tk in tickers):
		raise ValueError(f'Unknown tickers: {set(tk for tk in tickers if tk not in symbols_table)}')

	# if portfolio is not None:
	# 	if any(tk not in symbols_table for tk in portfolio):
	# 		raise ValueError(f'Unknown tickers: {set(tk for tk in portfolio if tk not in symbols_table)}')

	date = config.pull('date', 'last')
	date = str(date)

	# validity = config.pull('validity', 'last')
	features = config.pull('features')
	display_features = {}
	if isinstance(features, dict):
		display_features = features.copy()
		features = list(features.keys())

	table = []
	pop = []
	bad = {}

	ignore_errors = config.pull('ignore-errors', False)
	pbar = config.pull('pbar', True)

	config.print(f'Processing {len(tickers)} tickers')

	itr = tqdm(tickers) if pbar else tickers

	for yfsym in itr:
		if pbar:
			itr.set_description(f'{yfsym} (pop={len(pop)}, bad={len(bad)})')

		ctx = create_container(yfsym, date)

		try:
			table.append([ctx[feat] for feat in features])
		except Exception as e:
			if not ignore_errors:
				raise e
			else:
				bad[yfsym] = e
		else:
			pop.append(ctx)

	if len(bad):
		config.print(tabulate([(tk, type(err).__name__, str(err))
						for tk, err in bad.items()], headers=['ticker', 'error', 'message']))

		if not config.pull('ignore-bad', True):
			raise ValueError(f'Errors encountered: {bad}')

	if len(table) and outpath is not None:
		df = pd.DataFrame(table, columns=[display_features.get(feat, feat) for feat in features])
		df.to_csv(outpath, index=False)
		config.print(f'Saved {len(table)} rows to {outpath}')

	return pop












