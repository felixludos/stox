from .imports import *
from omnibelt import load_yaml

def stox_root():
	return Path(__file__).parent.parent

def get_secret(key):
	return load_yaml(stox_root() / 'config' / 'secrets.yml')[key]

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





















