from dataclasses import dataclass
from omnibelt import load_json, human_readable_number
from omniply import AbstractGadget, AbstractGig

from . import misc


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
		amount = self._humanize(self.amount)
		return f'{amount} {self.unit}'

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


from typing import Iterator, Optional, Any

class PopulationStats(AbstractGadget):
	def __init__(self, population: list[AbstractGig], *gizmos: str):
		super().__init__()
		self._population = population
		self._gizmos = gizmos

	def gizmos(self) -> Iterator[str]:
		yield from (f'pct_{gizmo}' for gizmo in self._gizmos)

	def grab_from(self, ctx: Optional[AbstractGig], gizmo: str) -> Any:
		key = gizmo[4:]

		mark = ctx[key]
		count = [(0.5 if item[key] == mark else (1 if item[key] < mark else 0))
				 for item in self._population if item[key] is not None]
		assert len(count) > 0, f'No values for {key}'
		return 100 * sum(count) / len(count)



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




























