


from omniply import novo
from omniply.novo.abstract import *
from omniply.novo.test_novo import CraftyKit, tool



class SymbolFinder(CraftyKit):
    @tool('ibsym')
    def yf2ib(self, yfsym):
        raise NotImplementedError

    @tool('yfsym')
    def ib2yf(self, ibsym):
        raise NotImplementedError















