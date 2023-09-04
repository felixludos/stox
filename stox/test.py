import random
from . import misc
from .ibkr import IBKR_Loader, IBKR_Stats, load_symbol_table
from omniply import tool, ToolKit, Context



def test_ibkr():
	symbol_table = load_symbol_table()
	# print(len(symbol_table))

	rows = [(k, v) for k, v in symbol_table.items() if v['currency'] == 'EUR']

	date = '230829'

	yfsym, ibrow = random.choice(rows)
	gg = Context(IBKR_Loader(date=date, root=misc.ibkr_root()), IBKR_Stats())
	gg.update(ibrow)
	gg['ibsym'] = ibrow['symbol']
	gg['ibid'] = ibrow['conId']
	gg['yfsym'] = yfsym

	print(yfsym)

	name = gg['company_name']

	land = gg['country']

	print(land)



