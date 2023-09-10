from pathlib import Path
from tqdm import tqdm
from tabulate import tabulate
import pandas as pd
from . import misc
from .yahoo import Yahoo_Downloader
from .ibkr import (load_symbol_table, IB_Extractor, IBKR_Downloader,
				   add_symbol_row, describe_contract, save_symbol_table)
import omnifig as fig



@fig.script('download')
def download_symbols(config):
	symbol_table = load_symbol_table()
	len(symbol_table)

	date = config.pull('date', misc.get_date())

	outpath = config.pull('outpath', 'download-results.yml')

	downloaders = config.pull('downloaders', {})
	assert len(downloaders), 'No downloaders specified'

	tickers = config.pull('tickers', None)
	if tickers is None:
		print('Downloading all tickers')
		tickers = list(symbol_table.keys())
	else:
		bad = [tk for tk in tickers if tk not in symbol_table]
		if len(bad):
			if 'ibkr' in downloaders:
				raise ValueError(f'Unknown tickers (for IBKR): {bad}')
			else:
				print(f'WARNING unknown tickers (for IBKR): {bad}')

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
		print(tabulate(failures, headers=['ticker', 'downloader', 'errors']))
	print(f'{num_new} reports successfully downloaded and {num_errors} errors.')

	if outpath is not None:
		misc.save_yaml(results, outpath)
	return results



@fig.script('add-ibsym')
def find_symbol(config):
	config.push('api._type', 'ib-extractor', silent=True, overwrite=False)
	ibe = config.pull('api')
	ibe.refresh()

	symbol_table = load_symbol_table()

	overwrite = True
	yfsym = config.pulls('yfsym', 'yf')
	if yfsym in symbol_table:
		overwrite = config.pulls('overwrite', 'f', default=False)
		print(f'{yfsym} already exists: {symbol_table[yfsym]}')

	secType = config.pull('secType', 'STK')
	currency = config.pulls('currency', 'm', default=None)

	srcs = []

	ibsym = config.pulls('ibsym', 'ib', default=None)
	if ibsym is not None:
		contract_info = {}
		if secType is not None:
			contract_info['secType'] = secType
		if currency is not None:
			contract_info['currency'] = currency
		cts = ibe.find_all_contracts(ibsym, **contract_info)
		srcs.append(cts)

	query = config.pulls('query', 'q', default=None)
	if ibsym is None and query is None:
		query = yfsym.split('.')[0]
	if query is not None:
		search_results = [c for c in ibe.search(query) if c.secType == secType]
		srcs.append(search_results)

	auto_select = config.pulls('auto-select', 'auto', default=False)

	assert len(srcs), f'No sources specified (provide at least one of "query" or "ibsym")'

	locs = [set(c.conId for c in src) for src in srcs]
	def score(ct):
		return (sum(ct.conId in loc for loc in locs),
				secType is None or ct.secType == secType,
				currency is None or ct.currency == currency,
				misc.str_similarity(yfsym.lower(), ct.symbol.lower()),
				)

	cts = sorted(set(ct for src in srcs for ct in src), key=score, reverse=True)

	if config.pull('return-all', False):
		return cts

	assert len(cts), 'No contracts found'

	index = config.pull('index', None)

	if index is None:
		print(tabulate([(i, yfsym, c.symbol, c.currency, c.primaryExchange, c.conId, c.description)
						for i, c in reversed(list(enumerate(cts)))]))
		print()

		if auto_select:
			ct = cts[0]
		else:
			idx = None
			while idx is None:
				raw = input('Select contract (index): ')
				try:
					idx = int(raw)
				except ValueError:
					print(f'Invalid index: {raw!r}')
			ct = cts[idx]
			print()

	else:
		ct = cts[index]

	ct = ibe.ib.reqContractDetails(ct)[0].contract

	if overwrite:
		print(f'Adding symbol {yfsym} {ct}')
		add_symbol_row(symbol_table, yfsym, ct, force=True)
		save_symbol_table(symbol_table)
	else:
		print(f'{yfsym} already exists: {symbol_table[yfsym]}')
		print('Not overwriting (set "overwrite" to overwrite)')

	print()
	describe_contract(ibe, ct)
	print()

	return ct



@fig.script('euro-stats')
def save_stats(config):
	container_source = config.peek('container')
	def create_container(yfsym, date):
		ctx = container_source.create()
		ctx['ticker'] = yfsym
		ctx['date'] = date
		return ctx

	outpath = config.pull('outpath', str(misc.assets_root()/'euro-stats.csv'))
	outpath = Path(outpath)
	if outpath.exists() and not config.pull('overwrite', False):
		print(f'File {outpath} already exists (use "overwrite" to overwrite)')
		return

	symbols_table = load_symbol_table()

	tickers = config.pull('tickers', None)
	if tickers is None:
		tickers = [sym for sym, info in symbols_table.items() if info.get('currency') == 'EUR']

	portfolio = config.pull('portfolio', None)
	if portfolio is None:
		portfolio_path = config.pull('portfolio-path', None)
		if portfolio_path is not None:
			portfolio = misc.extract_tickers_and_shares(portfolio_path)
			portfolio = {k: v for k, v in portfolio}

	if any(tk not in symbols_table for tk in tickers):
		raise ValueError(f'Unknown tickers: {set(tk for tk in tickers if tk not in symbols_table)}')

	if portfolio is not None:
		if any(tk not in symbols_table for tk in portfolio):
			raise ValueError(f'Unknown tickers: {set(tk for tk in portfolio if tk not in symbols_table)}')

	date = config.pull('date', 'last')

	# validity = config.pull('validity', 'last')
	features = config.pull('features')
	display_features = config.pull('display-features', {})

	table = []
	pop = []
	bad = {}

	pbar = config.pull('pbar', True)
	itr = tqdm(tickers) if pbar else tickers
	for yfsym in itr:
		if pbar:
			itr.set_description(f'{yfsym} (pop={len(pop)}, bad={len(bad)})')

		ctx = create_container(yfsym, date)

		try:
			table.append([ctx[feat] for feat in features])
		except Exception as e:
			bad[yfsym] = e
		else:
			pop.append(ctx)

	if len(bad):
		print(tabulate([(tk, type(err).__name__, str(err))
						for tk, err in bad.items()], headers=['ticker', 'error', 'message']))

		if not config.pull('ignore-bad', True):
			raise ValueError(f'Errors encountered: {bad}')

	if len(table) and outpath is not None:
		df = pd.DataFrame(table, columns=[display_features.get(feat, feat) for feat in features])
		df.to_csv(outpath, index=False)

	return pop












