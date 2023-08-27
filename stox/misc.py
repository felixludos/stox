from .imports import *
from omnibelt import load_yaml

def stox_root():
	return Path(__file__).parent.parent

def get_secret(key):
	return load_yaml(stox_root() / 'secrets.yml')[key]

def assets_root():
	'''Returns the root directory for the assets.'''
	return stox_root() / 'assets'

def data_root():
	'''Returns the root directory for the data.'''
	return stox_root() / 'data'

def yahoo_root():
	'''Returns the root directory for the Yahoo data.'''
	return data_root() / 'yahoo_data'

def ibkr_root():
	'''Returns the root directory for the IBKR data.'''
	return data_root() / 'ibkr_data'


def str_similarity(string1: str, string2: str):
	distance = Levenshtein.distance(string1, string2)
	similarity = 1 - (distance / max(len(string1), len(string2)))
	return similarity


def best_matches(options1: str | list[str], options2: str | list[str], similarity = str_similarity):
	'''Generates the best matches between two lists of options.'''
	if isinstance(options1, str):
		options1 = [options1]
	if isinstance(options2, str):
		options2 = [options2]
	results = [(similarity(option1, option2), option1, option2) for option1 in options1 for option2 in options2]
	yield from sorted(results, key=lambda x: x[0], reverse=True)


def extract_tickers_and_shares(file_path):
	'''Extracts a list of tickers from a text copy of the IBKR portfolio view.'''
	with open(file_path, 'r') as f:
		lines = f.readlines()

	results = []

	# Regular expression to match the pattern of the ticker followed by a number.
	pattern = re.compile(r'^([A-Z]+)\s+(\d+)')

	for line in lines:
		match = pattern.match(line.strip())
		if match:
			ticker = match.group(1)
			shares = int(match.group(2))
			results.append((ticker, shares))

	return results





















