from omnibelt import unspecified_argument
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from tabulate import tabulate

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import patches as mpatches

def make_find(world):
	if isinstance(world, list):
		world = {tk.ticker: tk for tk in world}
	def find(ident, tks=None):
		if tks is None:
			tks = world
		ident = ident.upper()
		if ident in tks:
			return tks[ident]
		prefixes = {k.split('.')[0]: v for k, v in tks.items()}
		if ident in prefixes:
			return prefixes[ident]
		raise KeyError(ident)
	
	return find
	
# model = manifold.MDS(n_components=2, random_state=0, metric='precomputed')
# coords = model.fit_transform(2-mat)
# colors = [seccolors[tk.info.get('sector')] for tk in tks]
# plt.figure(figsize=(7, 7))
# plt.scatter(coords[:, 0], coords[:, 1], marker='o', c=colors, s=50, edgecolor='None')
# plt.tight_layout()
# plt.axis('equal');
# # plt.show()

# # embedding = umap.UMAP(metric='correlation').fit_transform(fixed.T)
# model = umap.UMAP(n_neighbors=8, metric='precomputed').fit(2-mat)
# embedding = model.embedding_
# embedding.shape


# df = common.join_signals(tks, col='Close')
# pts = df
# pts = df[df.index.year == 2021]
# cr = pts.corr()
# pts = pts.to_numpy()
# mat = cr.to_numpy()

# np.argwhere(np.isnan(mat))

def join_signals(tks, col='Close'):
	df = None
	for tk in tks:
		sig = tk.history[col]
		if df is None:
			df = sig.rename(tk.ticker)
		else:
			df1, df2 = df, tk.history[col]
			df = pd.merge_asof(df1, df2, left_index=True, right_index=True, tolerance=pd.Timedelta("5m"))
			df.rename(columns={col: tk.ticker}, inplace=True)
	return df


base_sectors = [
	'Technology',
	'Healthcare',
	'Industrials',
	'Financials', # 'Financial Services'
	'Communication Services',
	'Consumer Discretionary', # 'Consumer Cyclical'
	'Consumer Staples', # 'Consumer Defensive'
	'Materials', # 'Basic Materials'
	'Utilities',
	'Energy',
	'Real Estate',
	'?',
]

sector_aliases = {
	'Financial': 'Financials',
'Consumer Cyclical': 'Consumer Discretionary',
	None:'?',
	0.:'?',
	0:'?',
	'0.':'?',
	'0.0':'?',
	'Services': 'Consumer Discretionary',
	'Industrial Goods': 'Industrials',
	'Consumer Goods': 'Consumer Staples',
'Financial Services': 'Financials',
'Consumer Defensive': 'Consumer Staples',
'Basic Materials': 'Materials',
}

{'Switzerland': '🇨🇭', 'Austria': '🇦🇹','Spain': '🇪🇸','Italy': '🇮🇹','Belgium': '🇧🇪','Netherlands': '🇳🇱','Germany': '🇩🇪',
 'Portugal': '🇵🇹','France': '🇫🇷', 'United Kingdom': '🇬🇧'}
sector_emojis = {
    'Consumer Staples': '🛒',# '🍎',
    'Financials': '💰', # '💵', #'🪙',
    'Utilities': '💧', #'🛁', # '🚿', # '🚰',
    'Technology': '📱', #'💻',
    'Energy': '🔥', #'🛢', # '⚡️'
    'Consumer Discretionary': '🎁', # '🛍'
    'Communication Services': '📞', # '📡',
    'Industrials': '⚙️',# '🔧', #'🏭',
    'Healthcare': '💊', #'💉',
    'Materials': '🌲', #'🧱', # '📦',
    'Real Estate': '🏠',
#     '?': '❓',
}

def html_tabulate(tbl, colors=None, tablefmt='html', **kwargs):
	rawtbl = tbl
	tbl = tabulate(tbl, tablefmt=tablefmt, **kwargs)
	if colors is not None:
		soup = BeautifulSoup(tbl)
		
		if isinstance(colors, str):
			colors = [colors] * len(rawtbl)
		if isinstance(colors, (list, tuple)) and (colors[0] is None or isinstance(colors[0], str)):
			colors = [[c] * len(rawtbl[0]) for c in colors]
		
		for (i, j), el in zip(np.ndindex(len(rawtbl), len(rawtbl[0])), soup.find_all('td')):
			color = colors[i][j]
			if 'style' in el.attrs:
				el['style'] = el.attrs['style'] + f'color:{color}'
			else:
				el['style'] = f'color:{color}'
		
		tbl = str(soup)
	return tbl


mpl_marks = ["o","v","^","<",">","8","s","p","P","*","h","H","X","D","d"]
mpl_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080']

feat_keys = [
	'currentPrice',
	'volume',
	'averageVolume', 'averageVolume10days',
	'marketCap',
	'dividendYield',
	'pegRatio',
	'beta',
	
	'priceToBook', 'payoutRatio',
	'priceToSalesTrailing12Months',
	'ebitdaMargins',
	
	'fiftyDayAverage', 'twoHundredDayAverage',
	
	'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
	'fullTimeEmployees',
	'heldPercentInsiders', 'heldPercentInstitutions',
	
	'earningsGrowth', 'revenueGrowth',
	'revenuePerShare',
	
	'profitMargins', 'totalCashPerShare',
	'operatingMargins', 'debtToEquity', 'grossMargins',
	'enterpriseToEbitda', 'enterpriseToRevenue',
	
	'trailingAnnualDividendYield', 'trailingEps', 'trailingPE',
	'forwardEps', 'forwardPE',
	
	'numberOfAnalystOpinions',
	'recommendationMean',
	'targetMeanPrice', 'targetMedianPrice',
	'targetLowPrice', 'targetHighPrice',
	
	'bookValue',
	'sharesOutstanding',
	'grossProfits', 'totalRevenue', 'totalDebt', 'totalCash', 'netIncomeToCommon', 'enterpriseValue',
	

]
feat_categoricals = [
	'country', 'city',
	
	'sector', 'industry',
	
	'quoteType',
	'exchange',
	'currency',

]

eye_brow_keys = ['adult', 'alcoholic', 'animalTesting', 'catholic', 'coal',
				 'furLeather', 'gmo', 'nuclear', 'palmOil', 'pesticides', ]
double_eye_brow_keys = ['controversialWeapons', 'militaryContract', 'gambling', 'smallArms', 'tobacco']
esg_scores = ['environmentScore', 'governanceScore', 'socialScore', 'totalEsg']
esg_percentiles = ['environmentPercentile', 'governancePercentile', 'socialPercentile', ]

def make_sustain_key(key):
	def _sustain_key(tk):
		try:
			val = tk.sustainability['Value'].to_dict()[key]
			if val is None:
				assert False
			return val
		except:
			pass
		return float('nan')
		return 0.
	
	_sustain_key.key = key
	return _sustain_key


def _eye_brow(tk):
	try:
		tbl = tk.sustainability['Value'].to_dict()
	except:
		pass
	else:
		return any(tbl.get(k) for k in eye_brow_keys)


def _double_eye_brow(tk):
	try:
		tbl = tk.sustainability['Value'].to_dict()
	except:
		pass
	else:
		return any(tbl.get(k) for k in double_eye_brow_keys)


def eye_brows(tk):
	try:
		tbl = tk.sustainability['Value'].to_dict()
	except:
		pass
	else:
		return [k for k in eye_brow_keys if tbl.get(k)], [k for k in double_eye_brow_keys if tbl.get(k)]
	return [], []


sustain_stats = {
	'eye-brow': _eye_brow,
	'double-eye-brow': _double_eye_brow,
	**{s: make_sustain_key(s) for s in esg_scores},
	**{s: make_sustain_key(s) for s in esg_percentiles},
}



def apply(fn, tickers, default=unspecified_argument):
	outs = [fn(tk) for tk in tickers]
	if default is not unspecified_argument:
		outs = [(default if o is None or o-o != 0 else o) for o in outs]
	return outs


def from_to(df, start=None, end=None):
	if start is None and end is None:
		return df
	start = True if start is None else (df.index >= start)
	end = True if end is None else (df.index < end)
	mask = start & end
	return df.loc[mask]

def total_return(df, auto_reinvest=False):
	if auto_reinvest:
		return (1 + (df['Dividends'] / df['Close']).sum()) * df['Close'][-1] / df['Open'][0]
	return (df['Close'][-1] + df['Dividends'].sum()) / df['Open'][0]




def make_versus_current(key, current='currentPrice', mn=None, mx=None):
	def _fn(tk):
		val = tk.info.get(key)
		if val is None:
			return float('nan')
			return 0.
		val =  tk.info[key] / tk.info[current]
		if mx is not None:
			val = min(mx, val)
		if mn is not None:
			val = max(mn, val)
		return val
	_fn.key = key
	return _fn

def make_info_key(key, log=False, mn=None, mx=None):
	def _info(tk):
		val = tk.info.get(key)
		if val is None:
			return float('nan')
			return 0.
		if log:
			val = np.log10(val)
		if mx is not None:
			val = min(mx, val)
		if mn is not None:
			val = max(mn, val)
		return val
	_info.key = key
	return _info

def make_total_return(start=None, end=None, auto_reinvest=False):
	def _return(tk):
		global from_to, total_return
		df = tk.history
		df = from_to(df, start=start, end=end)
		if len(df):
			return total_return(df, auto_reinvest=auto_reinvest)
		return float('nan')
		return 0.
	return _return

def fn_percentile(tk, fn, tks):
	return np.searchsorted(np.sort(apply(fn, tks)), fn(tk))/len(tks)*100


def plot_piece_pie(tks, nums, key='sector', colors=None, silent=True, explode=0.05, aliases={}, fgax=None, figsize=(9,5)):
	cats = apply(make_info_key(key), tks)
	cats = [aliases.get(str(cat), str(cat)) for cat in cats]
	groups = sorted(list(set(cats)))
	if colors is None:
		colors = {cat: mpl_colors[i%len(mpl_colors)] for i, cat in enumerate(groups)}
	cats, nums, names = zip(*sorted(zip(cats, nums, [tk.ticker for tk in tks])))
	explode = [explode] * len(cats)
	cs = [colors.get(cat,'w') for cat in cats]
	# ocs = [colors.get(o) for o in order]
	tots = {cat:0 for cat in groups}
	for cat, num in zip(cats, nums):
		tots[cat] += num
	if fgax is None:
		fgax = plt.subplots(figsize=figsize)
	fg, ax = fgax
	plt.sca(ax)
	plt.pie(nums, explode=explode, labels=names, autopct='%1.1f%%',
			colors=cs, startangle=0, normalize=True);
	plt.legend(handles=[mpatches.Patch(color=colors.get(cat, 'w'), label=f'{cat} ({tots[cat]*100:1.1f}%)')
	                    for cat in sorted(groups, key=lambda x: tots[x],reverse=True)],
			   loc='center left', bbox_to_anchor=(1.1, 0.5))
	plt.tight_layout();
	return fgax



# vals = get_info_key(key, tks, log=False, x100=False)
# # base = get_info_key('currentPrice', tks, log=False, x100=False)
# # vals /= base
#
# vals2 = get_info_key(key2, tks, log=False, x100=False)
# # vals = np.log10(vals)
# ok = np.isfinite(vals) * np.isfinite(vals2)
# print(f'Valid: {100*sum(ok)/len(ok):.0f}% ({sum(ok)}/{len(ok)})')

# cat_key = 'sector'
# cat_key = 'country'
# # cat_key = 'industry'
#
# cat_swaps = {None: 'Other', 'United Kingdom': 'Other', 'Luxembourg': 'Other', 'Switzerland': 'Other'}
#
# cats = apply(make_info_key(cat_key), tks)
# cats = np.array([cat_swaps.get(cat, cat) for cat in cats])
# gcats = sorted(set(c for c in cats if c is not None))
# cat_viz = {c: rcolors[i % len(rcolors)] for i, c in enumerate(gcats)}
# cat_titles = {}
# print(len(gcats), list(gcats))
#
# samples = [vals[(cats == cat) * ok] for cat in gcats]
# ysamples = [None for cat in gcats]
# ysamples = [vals2[(cats == cat) * ok] for cat in gcats]
# seq = sorted(zip(gcats, samples, ysamples), reverse=True, key=lambda x: x[1].mean())
# if False:
# 	fg, ax = plt.subplots()
# 	plt.hist([x[1] for x in seq],
# 	         bins=120,
# 	         stacked=True, label=[f'{cat} ({np.mean(x):.3g})' for cat, x, y in seq])
# 	plt.xlabel(key)
# 	plt.ylabel('Count')
# 	plt.legend()
# 	plt.tight_layout();
#
# fg, ax = plt.subplots()
# for i, (cat, x, y) in enumerate(seq):
# 	plt.plot(x, y, ls='', marker='o', color=cat_viz[cat], label=cat, zorder=len(seq) - i + 1)
# plt.xlabel(key)
# plt.ylabel(key2)
# plt.legend()
# # handles = [mpatches.Patch(color=cat_viz[c], label=cat) for c,_ in seq]
# # cleg = plt.legend(handles, cats, loc=3)
# plt.tight_layout();
#
# # print(tabulate([(n,xs.mean()) for n, xs in seq][:50]))


# tk = random.choice(options)
# tk.ticker
# df = tk.history
# df = common.from_to(df, start='2020-12-01', end='2021-12-01')
# df.shape
# df['Close'][-1]/df['Open'][0], common.total_return(df), common.total_return(df, auto_reinvest=True)

# stats = []
# for tk in tqdm(options):
#     df = tk.history
#     df = common.from_to(df, start='2021-01-01', end='2022-01-01')
#     if len(df) > 250:
#         stats.append([df['Close'][-1]/df['Open'][0], common.total_return(df), common.total_return(df, auto_reinvest=True)])
# stats = np.array(stats)
# stats.shape



# tk.earnings
# tk.quarterly_earnings
# profit = tk.info['totalRevenue']
# profit
# tk.info['earningsGrowth']
# profit / e[-1]
# e = tk.earnings['Revenue'].to_numpy()
# # e = tk.quarterly_earnings['Revenue'].to_numpy()
# e
# x = np.arange(len(e))
# m, y0, *other = linregress(x, e)
# m
# plt.figure()
# plt.plot(x, e, ls='', marker='o')
# plt.plot(x, y0+m*x);
# m / x[-1]
# import networkx as nx
# plt.figure(figsize=(7, 7))
#
# dt = [('len', float)]
# A = delta
# A = A.view(dt)
#
# G = nx.from_numpy_matrix(A)
# pos = nx.spring_layout(G)
#
# nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=50)
#
# lgd = plt.legend(markers, labels, numpoints=1, bbox_to_anchor=(1.17, 0.5))
# plt.tight_layout()
# plt.axis('equal')
# plt.show()
#
#
# cmap = plt.get_cmap('Set1')
# # colors = [cmap(i) for i in numpy.linspace(0, 1, simulations)]
#
# plt.figure(figsize=(7, 7))
# plt.scatter(coords[:, 0], coords[:, 1], marker='o', c=colors, s=50, edgecolor='None')
#
# markers = []
# labels = [str(n+1) for n in range(simulations)]
# # for i in range(simulations):
# #     markers.append(Line2D([0], [0], linestyle='None', marker="o", markersize=10, markeredgecolor="none", markerfacecolor=colors[i]))
# lgd = plt.legend(markers, labels, numpoints=1, bbox_to_anchor=(1.17, 0.5))
# plt.tight_layout()
# plt.axis('equal')
# plt.show()
#
# coords
#
# df1, df2 = tks[0].history[col], tks[1].history[col]
# # df1, df2 = df1.rename({col:tks[0].ticker}), df2.rename({col:tks[1].ticker})
# df = pd.merge_asof(df1, df2, left_index=True, right_index=True, tolerance=pd.Timedelta("5m"))
# df.rename(columns={f'{col}_x':tks[0].ticker, f'{col}_y':tks[1].ticker}, inplace=True)
# df
#
# df[df.index.year == 2021].corr()


# from IPython.display import HTML as html_print
#
# def cstr(s, color='black'):
#     return "<text style=color:{}>{}</text>".format(color, s)
#
# left, word, right = 'foo' , 'abc' , 'bar'
# html_print(cstr(' '.join([left, cstr(word, color=common.mpl_colors[1]), right]), color='black') )
















