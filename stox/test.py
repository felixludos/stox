import random
from . import misc
from .ibkr import IBKR_Loader, IBKR_Stats, IBKR_Derived, load_symbol_table
from .yahoo import Yahoo_Loader, Yahoo_Info
from omniply import tool, ToolKit, Context, Scope, Selection



def test_ibkr():
	symbol_table = load_symbol_table()
	# print(len(symbol_table))

	rows = [(k, v['ibkr-contract']) for k, v in symbol_table.items() if v['ibkr-contract']['currency'] == 'EUR']

	date = '230829'

	yfsym, ibrow = random.choice(rows)
	gg = Context(
		Scope(IBKR_Derived(), IBKR_Stats(), IBKR_Loader(root=misc.ibkr_root()),
			  gap={
				  'ckpt_path': 'ib_ckpt_path',
			  }),
		Selection(Yahoo_Info(), Yahoo_Loader(root=misc.yahoo_root()),
			  gap={
				  'ckpt_path': 'yahoo_ckpt_path',
				  'ticker': 'yfsym',

				  'info': 'info',
				  'splits': 'splits',

				  'recommendation_mean': 'recommendation_mean',
				  'recommendation_key': 'recommendation_key',
				  'number_of_analysts': 'number_of_analysts',
				  'target_mean_price': 'target_mean_price',
				  'target_high_price': 'target_high_price',
				  'target_low_price': 'target_low_price',
				  'target_median_price': 'target_median_price',
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

	rec = gg['recommendation_mean']
	print(rec)



