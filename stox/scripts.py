from pathlib import Path
from tqdm import tqdm
from tabulate import tabulate
from . import misc
from .yahoo import download as yfdownload
from .ibkr import load_symbol_table, IB_Extractor, download_reports
import omnifig as fig




@fig.script('download')
def download_symbols(config):
	symbol_table = load_symbol_table()
	len(symbol_table)

	date = None

	yahoo = config.pull('yahoo', True)
	if yahoo:
		yfroot = config.pull('yahoo-root', str(misc.yahoo_root()))
		yfroot = Path(yfroot)
		yfroot.mkdir(exist_ok=True, parents=True)

	ibkr = config.pull('ibkr', True)
	if ibkr:
		ibroot = config.pull('ibkr-root', str(misc.ibkr_root()))
		ibroot = Path(ibroot)
		ibroot.mkdir(exist_ok=True, parents=True)

		ibe = IB_Extractor()

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

	bad_yf, bad_ib = {}, {}

	pbar = config.pull('pbar', True)
	itr = tickers
	if pbar:
		itr = tqdm(itr)
	for ticker in itr:
		if pbar:
			itr.set_description(ticker)

		if yahoo:
			failures = yfdownload(ticker, date=date, root=yfroot, pbar=None)
			if len(failures):
				bad_yf[ticker] = list(failures)

		if ibkr:
			failures = download_reports(symbol_table[ticker], date=date, root=ibroot, pbar=None)
			if len(failures):
				bad_ib[ticker] = list(failures)

	if len(bad_yf):
		print(tabulate(bad_yf.items(), headers=['ticker', 'failures']))
		print(f'Failed to download {len(bad_yf)} yahoo.')
		print(list(bad_yf.keys()))

	if len(bad_ib):
		print(tabulate(bad_ib.items(), headers=['ticker', 'failures']))
		print(f'Failed to download {len(bad_ib)} ibkr.')
		print(list(bad_ib.keys()))

	return bad_yf, bad_ib





















