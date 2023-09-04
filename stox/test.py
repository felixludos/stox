import random
from . import misc
from .ibkr import IBKR_Loader, IBKR_Stats, IBKR_Derived, load_symbol_table
from .yahoo import Yahoo_Loader
from omniply import tool, ToolKit, Context, Scope



def test_ibkr():
	symbol_table = load_symbol_table()
	# print(len(symbol_table))

	rows = [(k, v) for k, v in symbol_table.items() if v['currency'] == 'EUR']

	date = '230829'

	yfsym, ibrow = random.choice(rows)
	gg = Context(
		Scope(IBKR_Derived(), IBKR_Stats(), IBKR_Loader(root=misc.ibkr_root()),
			  apply={
				  'ckpt_path': 'ib_ckpt_path',
			  }),
		Scope(Yahoo_Loader(root=misc.yahoo_root()),
			  apply={
				  'ckpt_path': 'yahoo_ckpt_path',
			  }),
	)

	gg.update(ibrow)
	gg['date'] = date
	gg['ibsym'] = ibrow['symbol']
	gg['ibid'] = ibrow['conId']
	gg['yfsym'] = yfsym

	print(yfsym)

	name = gg['company_name']

	land = gg['country']

	print(land)



