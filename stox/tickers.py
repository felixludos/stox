from .imports import *

from omniply.novo.test_novo import CraftyKit, tool



class SymbolFinder(CraftyKit):
	def __init__(self, path: Path, **kwargs):
		super().__init__(**kwargs)
		self.path = path

	def load(self):
		self.raw_data = load_export(self.path)
		self.from_yf = {v['yfsym']: v for v in self.raw_data.values()
						if v['yfsym'] is not None}
		self.from_ib = {v['ibsym']: v for v in self.raw_data.values()
						if v['ibsym'] is not None}

	@tool('ibsym')
	def yf2ib(self, yfsym: str):
		return self.from_yf[yfsym]['ibsym']
	
	@tool('yfsym')
	def ib2yf(self, ibsym: str):
		return self.from_ib[ibsym]['yfsym']









