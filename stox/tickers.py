from .imports import *


class SymbolFinder(CraftyKit):
	@tool('ibsym')
	def yf2ib(self, yfsym):
		raise NotImplementedError
	
	@tool('yfsym')
	def ib2yf(self, ibsym):
		raise NotImplementedError









