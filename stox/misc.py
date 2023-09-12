from .imports import *
from omnibelt import load_yaml, human_readable_number
from datetime import datetime
from unidecode import unidecode


safe_noise_words = {"PLC", "AG", "CORP", "NV", "SA", "INC", "SE", "ADR", "OYJ", "SPA", "SME", "GROEP", "SOCIETE", "GROUP",
    "EO", "NA", "ON", "O", "N", "S", "A", "CR", "CO", "EO", "group", "plc", "inc", "corp", "sa", "ag", "eo", "gmbh", "ltd", "llc", "n.v", "nv",}
noise_words = { *safe_noise_words,
     "-", ",", ".", "&", "AND", "HOLDINGS", "INTERNATIONAL",
	"kgaa", "se", "oao", "ab", "asa", "s.p.a", "spa", "co", "sl", "p.l.c.", "bv", "lp", "srl", "oyj", "l.p.", "rl", "p.c.", 'n.v', 'n.v.', 's.a.', 's.a', 'ny', 'n.y.', 'n.y', 's.p.a.', '(cr)', '(publ)', 'Sgps', 'St',
		'Inh.', 'O.n.', 's.e.', 'Dr.', 'Ing.', 'H.c.', 'F.', 'Aktiengesellschaft', 'company', 'corporation', 'R', 'gr', 'inh', 'ord', 'c', 'v', 'p', 'e', 'h'}
noise_words = {w.lower() for w in noise_words}
noise_words.update({w.replace('.', '') for w in noise_words})
safe_noise_words = {w.lower() for w in safe_noise_words}
safe_noise_words.update({w.replace('.', '') for w in safe_noise_words})
def clean_company_name(name):
	name = unidecode(name)
	name = name.replace('/', ' ').replace('-', ' ').replace('+', ' ').replace(',', ' ').replace('.', '')
	fixed = ' '.join(w.capitalize().replace('.', ' ').strip() for w in name.split() if w.lower() not in noise_words).strip()
	if not len(fixed):
		return ' '.join(w.capitalize().replace('.', ' ').strip() for w in name.split() if w.lower() not in safe_noise_words).strip()
	return fixed


humanize = human_readable_number


STD_FMT = "%y%m%d"

def get_date(fmt=None):
	if fmt is None:
		fmt = STD_FMT
	return datetime.now().strftime(fmt)


def get_date_path(root, ticker: str, date=None):
	'''ticker should be the yahoo finance ticker'''
	ticker = ticker.replace('.', '_').replace('-', '_').replace(' ', '_')
	tickerroot = root / ticker
	tickerroot.mkdir(exist_ok=True)
	if date == 'last':
		options = sorted(tickerroot.glob('*'), key=lambda p: p.name)#[-1]
		if len(options):
			date = options[-1]
		else:
			date = None
	if date is None:
		date = get_date()
	path = tickerroot / date
	path.mkdir(exist_ok=True)
	return path



def stox_root():
	return Path(__file__).parent.parent

def get_secret(key):
	return load_yaml(stox_root() / 'secrets.yml')[key]

def assets_root():
	'''Returns the root directory for the assets.'''
	return stox_root() / 'assets'

def data_root():
	'''Returns the root directory for the data.'''
	return stox_root() / 'stoxdata'

def yahoo_root():
	'''Returns the root directory for the Yahoo data.'''
	return data_root() / 'yahoo_data'

def ibkr_root():
	'''Returns the root directory for the IBKR data.'''
	return data_root() / 'ibkr_data'

def alpha_vantage_root():
	'''Returns the root directory for the Alpha Vantage data.'''
	return data_root() / 'alpha_vantage_data'


def str_similarity(string1: str, string2: str):
	distance = Levenshtein.distance(string1, string2)
	similarity = 1 - (distance / max(len(string1), len(string2)))
	return similarity


def best_matches(options1: str | Iterable[str], options2: str | Iterable[str], *, similarity = str_similarity,
				 key1=None, key2=None):
	'''Generates the best matches between two lists of options.'''
	keys1 = options1 if key1 is None else list(map(key1, options1))
	keys2 = options2 if key2 is None else list(map(key2, options2))
	results = [(similarity(s1, s2), option1, option2)
			   for s1, option1 in zip(keys1, options1)
			   for s2, option2 in zip(keys2, options2)]
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





















