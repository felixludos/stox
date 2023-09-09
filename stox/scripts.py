from pathlib import Path
from tqdm import tqdm
from tabulate import tabulate
from . import misc
from .yahoo import Yahoo_Downloader
from .ibkr import load_symbol_table, IB_Extractor, IBKR_Downloader
import omnifig as fig




@fig.script('download')
def download_symbols(config):
	symbol_table = load_symbol_table()
	len(symbol_table)

	date = None

	outpath = config.pull('outpath', 'download-results.yml')

	downloaders = config.pull('downloaders', {})

	yahoo = config.pull('yahoo', 'yahoo' not in downloaders)
	if yahoo:
		yfroot = config.pull('yahoo-root', str(misc.yahoo_root()))
		yfroot = Path(yfroot)
		yfroot.mkdir(exist_ok=True, parents=True)
		downloaders['yahoo'] = Yahoo_Downloader(root=yfroot)

	ibkr = config.pull('ibkr', 'ibkr' not in downloaders)
	if ibkr:
		ibroot = config.pull('ibkr-root', str(misc.ibkr_root()))
		ibroot = Path(ibroot)
		ibroot.mkdir(exist_ok=True, parents=True)
		downloaders['ibkr'] = IBKR_Downloader(root=ibroot)

	tickers = config.pull('tickers', None)
	if tickers is None:
		print('Downloading all tickers')
		tickers = list(symbol_table.keys())
	else:
		bad = [tk for tk in tickers if tk not in symbol_table]
		if len(bad):
			if ibkr:
				raise ValueError(f'Unknown tickers (for IBKR): {bad}')
			else:
				print(f'WARNING unknown tickers (for IBKR): {bad}')

	results = {}

	pbar = config.pull('pbar', True)
	itr = tickers
	if pbar:
		itr = tqdm(itr)
	for ticker in itr:
		for name, downloader in downloaders.items():
			if pbar:
				itr.set_description(f'{ticker} :: {name}')
			reports = downloader.download_reports(ticker, pbar=None, date=date)
			results.setdefault(ticker, {})[name] = {k: repr(v) for k, v in reports.items() if isinstance(v, Exception)}

	failures = [(tk, name, '\n'.join(f'{k} : {v}' for k,v in errs))
				for tk, dls in results.items() for name, errs in dls.items()]
	if len(failures):
		print(tabulate(failures, headers=['ticker', 'downloader', 'errors']))
		print(f'Errors with {len(failures)} tickers+downloaders.')

	if outpath is not None:
		misc.save_yaml(results, outpath)
	return results





















