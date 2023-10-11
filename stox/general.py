import math
from typing import Iterator, Optional, Any
from dataclasses import dataclass
from omnibelt import load_json, human_readable_number, unspecified_argument, load_yaml
import omnifig as fig
from omniply import (AbstractGadget, AbstractGig, GadgetFailure, ToolKit, tool,
					 Scope as _Scope, Context as _Context, Selection as _Selection)
from . import misc



def load_symbol_table():
	root = misc.assets_root()
	path = root / 'symbol-table.yml'
	data = load_yaml(path)
	return data





@fig.component('scope')
class Scope(_Scope, fig.Configurable):
	def __init__(self, gadgets = None, gap = None, **kwargs):
		if gadgets is None:
			gadgets = []
		if isinstance(gadgets, dict):
			gadgets = list(gadgets.values())
		super().__init__(*gadgets, gap=gap, **kwargs)



@fig.component('selection')
class Selection(_Selection, fig.Configurable):
	def __init__(self, gadgets = None, **kwargs):
		if gadgets is None:
			gadgets = []
		if isinstance(gadgets, dict):
			gadgets = list(gadgets.values())
		super().__init__(*gadgets, **kwargs)



@fig.component('context')
class Context(_Context, fig.Configurable):
	def __init__(self, gadgets = None, cache = None, **kwargs):
		if gadgets is None:
			gadgets = []
		if isinstance(gadgets, dict):
			gadgets = list(gadgets.values())
		super().__init__(*gadgets, **kwargs)
		if cache is not None:
			self.update(cache)



sector_colors = {
    "Technology": "#6495ED",  # Cornflower Blue
    "Health Care": "#2E8B57",  # Sea Green
    "Financials": "#FFD700",  # Gold
    "Consumer Discretionary": "#DC143C",  # Crimson
    "Consumer Staples": "#FFA500",  # Orange
    "Energy": "#FFD300",  # Bright Yellow
    "Utilities": "#20B2AA",  # Light Sea Green
    "Industrials": "#800080",  # Purple
    "Materials": "#8B4513",  # Saddle Brown
    "Real Estate": "#FF69B4",  # Hot Pink
    "Communication Services": "#98FB98",  # Pale Green
	'None': '#999999',
}



country_flags = {
	'Switzerland': '🇨🇭',
	'Austria': '🇦🇹',
	'Spain': '🇪🇸',
	'Italy': '🇮🇹',
	'Belgium': '🇧🇪',
	'Netherlands': '🇳🇱',
	'Greece': '🇬🇷',
	'Germany': '🇩🇪',
	'Portugal': '🇵🇹',
	'France': '🇫🇷',
	'United Kingdom': '🇬🇧',
	'Finland': '🇫🇮',
	'Sweden': '🇸🇪',
	'Luxembourg': '🇱🇺',
	'Norway': '🇳🇴',
}

sector_emojis = {
    'Consumer Staples': '🛒',# '🍎',
    'Consumer Defensive': '🛒',# '🍎',
    'Financial Services': '🪙',# '💰', # '💵',
    'Financials': '🪙',
    'Utilities': '💧', #'🛁', # '🚿', # '🚰',
    'Technology': '📱', #'💻',
    'Energy': '🔥', #'🛢', # '⚡️'
    'Consumer Cyclical': '🎁', # '🛍'
    'Consumer Discretionary': '🎁', # '🛍'
    'Communication Services': '📞', # '📡',
    'Industrials': '⚙️',# '🔧', #'🏭',
    'Healthcare': '💊', #'💉',
    'Basic Materials': '🌲', #'🧱', # '📦',
    'Materials': '🌲', #'🧱', # '📦',
    'Real Estate': '🏠',
#     '?': '❓',
}

country_colors = {
    'France': 'blue',
    'Germany': 'grey',
    'Italy': 'green',
    'Spain': 'red',
    'Belgium': 'yellow',
    'Netherlands': 'orange',
    'Greece': 'skyblue',
    'Austria': 'darkred',
    'Finland': 'cyan',
    'United Kingdom': 'darkblue',
    'Switzerland': 'lightcoral',
    'Luxembourg': 'royalblue',
    'Portugal': 'darkgreen',
    'Sweden': 'gold'
}


sector_symbols = {
    'Industrials': 'circle',
    'Financial Services': 'diamond',
    'Consumer Cyclical': 'triangle-up',
    'Utilities': 'square',
    'Basic Materials': 'pentagon',
    'Consumer Defensive': 'triangle-down',
    'Technology': 'star',
    'Healthcare': 'cross',
    'Communication Services': 'star-diamond',
    'Real Estate': 'hexagon',
    'Energy': 'octagon'
}


country_colors_hex = {
    'France': '#0000FF',       # blue
    'Germany': '#808080',     # grey
    'Italy': '#008000',       # green
    'Spain': '#FF0000',       # red
    'Belgium': '#FFFF00',     # yellow
    'Netherlands': '#FFA500', # orange
    'Greece': '#87CEEB',      # skyblue
    'Austria': '#8B0000',     # darkred
    'Finland': '#00FFFF',     # cyan
    'United Kingdom': '#00008B', # darkblue
    'Switzerland': '#F08080', # lightcoral
    'Luxembourg': '#4169E1',  # royalblue
    'Portugal': '#006400',    # darkgreen
    'Sweden': '#FFD700'       # gold
}



@dataclass
class Quantity:
	amount: float
	unit: str

	def _humanize(self, amount):
		return human_readable_number(amount, significant_figures=3)

	def __str__(self):
		amount = self._humanize(self.amount)
		return f'{amount} {self.unit}'

	def __repr__(self):
		return str(self)

	def __lt__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount < other.amount

	def __le__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount <= other.amount

	def __eq__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount == other.amount

	def __ne__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount != other.amount

	def __gt__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount > other.amount

	def __ge__(self, other):
		assert isinstance(other, Quantity) and self.unit == other.unit, f'Cannot compare {self} to {other}'
		return self.amount >= other.amount


class PctChange(Quantity):
	def __init__(self, amount: float):
		super().__init__(amount, '%')

	def __str__(self):
		prefix = '+' if self.amount > 0 else ''
		return f'{prefix}{super().__str__()}'



class Downloader:
	def __init__(self, root=None, **kwargs):
		super().__init__(**kwargs)
		self.root = root

	def valid_ticker(self, ticker):
		return True

	def report_keys(self):
		raise NotImplementedError

	def report_path(self, ticker, key, date=unspecified_argument):
		raise NotImplementedError

	def download_reports(self, ticker, *, keys=None, pbar=None, date=unspecified_argument):
		raise NotImplementedError

	def load_report(self, ticker, key, date=unspecified_argument):
		raise NotImplementedError



@fig.component('portfolio-loader')
class PortfolioLoader(ToolKit, fig.Configurable):
	def __init__(self, *, name=None, root=None, path=None, **kwargs):
		if path is None:
			if root is None:
				root = misc.assets_root() / 'ibkr'
			if name is not None:
				path = root / name
		super().__init__(**kwargs)
		self.portfolio = {'ITX.MC': 34, 'RACE.MI': 5, 'ARGX.BR': 2, 'SAP.DE': 10, 'PRX.AS': 16, 'ASML.AS': 3, 'MC.PA': 2, 'ETE.AT': 95, 'AIR.PA': 9, 'PHIA.AS': 41, 'LIN.DE': 3, 'SU.PA': 5, 'SIE.DE': 8, 'BBVA.MC': 45, 'IIA.VI': 20, 'ENEL.MI': 139, 'STMPA.PA': 12, 'ISP.MI': 130, 'IAG.MC': 280, 'ALV.DE': 5, 'SAN.PA': 13, 'BNP.PA': 9, '0EXG.IL': 22, 'REN.AS': 23, 'EBS.VI': 23, 'AI.PA': 5, 'KER.PA': 2, 'TTE.PA': 3, 'IFX.DE': 9, 'HO.PA': 2, 'UCB.BR': 3, 'DTE.DE': 7, 'AMS.MC': 11, 'AD.AS': 8, 'CS.PA': 15, 'ENI.MI': 28, 'SHELL.AS': 8, 'LHA.DE': 24, 'KBC.BR': 9, 'ABI.BR': 3, 'RBI.VI': 45, 'BAS.DE': 6, 'UBI.PA': 18, 'ATS.VI': 20, 'IBE.MC': 102, 'MRL.MC': 40, 'TEN.MI': 21, 'OMV.VI': 5, 'MRK.DE': 5, 'ZAL.DE': 12, 'BAYN.DE': 8, 'CNHI.MI': 28, 'VER.VI': 14, 'NEXI.MI': 40, 'WDP.BR': 25, 'NOKIA.HE': 198, 'VNA.DE': 19, 'UNA.AS': 6, 'BMW.DE': 2, 'FORTUM.HE': 15, 'DTG.DE': 5}
		if path is not None and path.exists():
			if self.portfolio is not None:
				raise ValueError('Cannot specify both path and portfolio')
			symbols_table = load_symbol_table()
			ib2yf = {v['ibkr-contract']['symbol']: k for k, v in symbols_table.items()}
			portfolio_list = misc.extract_tickers_and_shares(path)
			portfolio = dict(portfolio_list)
			assert len(portfolio) == len(portfolio_list), f'Duplicate tickers in {path}'
			self.portfolio = {ib2yf[k]: v for k, v in portfolio.items()}


	@tool('shares')
	def number_of_shares(self, ticker):
		if self.portfolio is None:
			return None
		return self.portfolio.get(ticker, 0)



@fig.component('common-stats')
class Common_Stats(ToolKit, fig.Configurable):
	@tool('log_market_cap')
	def get_log_market_cap(self, market_cap: Quantity):
		if market_cap is None or market_cap.amount is None:
			return None
		return math.log10(market_cap.amount)

	@tool('raw_market_cap')
	def get_raw_market_cap(self, market_cap: Quantity):
		if market_cap is None or market_cap.amount is None:
			return None
		return market_cap.amount



class PopulationStats(AbstractGadget):
	def __init__(self, population: list[AbstractGig], *gizmos: str, percentile=False, location=True):
		super().__init__()
		self._population = population
		self._gizmos = gizmos
		self._location = location
		self._percentile = percentile

	def gizmos(self) -> Iterator[str]:
		if self._location:
			yield from (f'loc_{gizmo}' for gizmo in self._gizmos)
		if self._percentile:
			yield from (f'pct_{gizmo}' for gizmo in self._gizmos)


	def _base_stats(self, pop, key):
		for item in pop:
			val = item[key]
			if val is not None and (not isinstance(val, Quantity) or val.amount is not None):
				yield val


	def compute_pct(self, mark: Any, key: str) -> float:
		count = [(0.5 if val == mark else (1 if val < mark else 0))
				 for val in self._base_stats(self._population, key) if val is not None]
		assert len(count) > 0, f'No values for {key}'
		return int(100 * sum(count) / len(count))

	def compute_loc(self, mark: Any, key: str) -> str:
		count = [(0.5 if val == mark else (1 if val < mark else 0))
				 for val in self._base_stats(self._population, key) if val is not None]
		assert len(count) > 0, f'No values for {key}'
		return f'{int(sum(count))}/{len(count)}'

	def grab_from(self, ctx: Optional[AbstractGig], gizmo: str) -> Any:
		if self._percentile and gizmo.startswith('pct_'):
			key = gizmo[4:]
			mark = ctx[key]
			return self.compute_pct(mark, key)
		if self._location and gizmo.startswith('loc_'):
			key = gizmo[4:]
			mark = ctx[key]
			return self.compute_loc(mark, key)
		raise GadgetFailure(gizmo)


class PopulationStats(AbstractGadget):
	def __init__(self, population: list, *gizmos: str, percentile=False, location=True):
		super().__init__()
		self._population = population
		self._gizmos = gizmos
		self._location = location
		self._percentile = percentile

	def gizmos(self) -> Iterator[str]:
		if self._location:
			yield from (f'loc_{gizmo}' for gizmo in self._gizmos)
		if self._percentile:
			yield from (f'pct_{gizmo}' for gizmo in self._gizmos)


	def _base_stats(self, pop, key):
		for item in pop:
			val = item[key]
			if val is not None and (not isinstance(val, Quantity) or val.amount is not None):
				yield val


	def compute_pct(self, mark, key: str) -> float:
		if mark is None or (isinstance(mark, Quantity) and mark.amount is None):
			return None
		count = []
		vals = list(self._base_stats(self._population, key))
		for val in vals:
			if val is not None:
				if val == mark:
					count.append(0.5)
				elif val < mark:
					count.append(1)
				else:
					count.append(0)
		assert len(count) > 0, f'No values for {key}'
		return int(100 * sum(count) / len(count))

	def compute_loc(self, mark, key: str) -> str:
		if mark is None or (isinstance(mark, Quantity) and mark.amount is None):
			return None
		count = []
		vals = list(self._base_stats(self._population, key))
		for val in vals:
			if val is not None:
				if val == mark:
					count.append(0.5)
				elif val < mark:
					count.append(1)
				else:
					count.append(0)
		assert len(count) > 0, f'No values for {key}'
		return f'{int(sum(count))}/{len(count)}'

	def grab_from(self, ctx, gizmo: str):
		if self._percentile and gizmo.startswith('pct_'):
			key = gizmo[4:]
			mark = ctx[key]
			return self.compute_pct(mark, key)
		if self._location and gizmo.startswith('loc_'):
			key = gizmo[4:]
			mark = ctx[key]
			return self.compute_loc(mark, key)
		raise NotImplementedError


class TRBC_Codes:
	def __init__(self, path=None):
		if path is None:
			path = misc.assets_root() / 'trbc_codes.json'
		self.full_data = load_json(path)
		self.trbc_to_name = {item['TRBC ID']: item['Name'] for item in self.full_data}


	def get_classification_hierarchy(self, trbc_code):
		"""
		Get the hierarchy of classifications based on the TRBC code.

		Args:
		- trbc_code (str): The TRBC code.

		Returns:
		- tuple: A tuple containing the hierarchy of classifications.
		"""
		hierarchy = []

		while trbc_code:
			name = self.trbc_to_name.get(trbc_code)
			if not name:
				break
			hierarchy.insert(0, name)
			trbc_code = trbc_code[:-2]  # Remove two characters at a time

		return tuple(hierarchy)


	def get_sector(self, trbc_code):
		return self.get_classification_hierarchy(trbc_code)[0]




























