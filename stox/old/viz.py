
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.figure import figaspect

def dicts_to_table(data, typs={}, sort_by=None, cols=None, reverse=False, default=None, ignore_key=False, skip_header=False):
	
	# def_types = {str:'', float:0., int:0}
	
	if cols is None:
		cols = set()
		for row in data.values():
			cols.update(row.keys())
		cols = list(cols)
	
	header = [] if ignore_key else ['Ticker']
	header.extend(cols)
	
	tbl = []
	
	for k, row in data.items():
		
		# info = {name :default for name in cols}
		
		info = {}
		for prop, val in row.items():
			if prop in typs:
				ok = typs[prop]
				if prop in typs and not isinstance(val, ok):
					val = default
					# try:
					# 	typ = typs[prop][0] if isinstance(typs[prop], tuple) else typs[prop]
					# 	val = typ(val)
					# except ValueError:
					# 	val = default
						# val = def_types.get(typs[prop], default)
			info[prop] = val
		
		for c in cols:
			if c not in info:
				info[c] = default
		
		row = [] if ignore_key else [k]
		row.extend(info[c] for c in cols)
		tbl.append(row)
	
	if sort_by is not None:
		inds = {n :i for i, n in enumerate(header)}
		idx = inds[sort_by]
		tbl = sorted(tbl, key=lambda x: (x[idx] is not None, x[idx]), reverse=reverse)
	
	table = [] if skip_header else [header]
	table.extend(tbl)
	return table

def get_top(data, top=None, factor=100):
	tb = [(k,v*factor if v is not None else v) for k,v in data.items()]
	tb = sorted(tb, key=lambda x: (x[1] is not None, x[1]), reverse=True)
	if top is not None:
		top = tb[:top]
		top.append(('Other', sum(q for _,q in tb) - sum(q for _,q in top)))
		tb = top
	return tb

def plot_parallel_coords(samples, categories=None, dim_names=None,
						 cat_styles=None, cat_names=None, include_legend=True,
						 mins=None, maxs=None,
						 figax=None, figsize=(8, 5), **default_style):
	'''
	samples: (N,D)
	categories: (N,)

	Example:

	from sklearn import datasets
	iris = datasets.load_iris()
	plot_parallel_coords(iris.data, dim_names=iris.feature_names,
						 categories=[iris.target_names[i] for i in iris.target])

	'''
	N, D = samples.shape
	
	classes = None
	if categories is not None:
		assert len(categories) == N, f'{len(categories)} vs {N}'
		
		classes = set(categories)
		if cat_names is not None:
			classes = cat_names
		K = len(classes)
		sep_classes = False
		if cat_styles is None:
			sep_classes = True
			cat_styles = {c: default_style.copy() for c in classes}
		
		for i, (name, style) in enumerate(cat_styles.items()):
			if 'color' in style and 'edgecolor' not in style:
				style['edgecolor'] = style['color']
				del style['color']
			elif sep_classes and 'edgecolor' not in style:
				style['edgecolor'] = f'C{i}'
			if 'facecolor' not in style:
				style['facecolor'] = 'none'
	
	try:
		samples = samples.cpu().numpy()
	except:
		pass
	
	if dim_names is None:
		dim_names = ['{}'.format(i) for i in range(D)]
	
	ynames = dim_names
	ys = samples
	
	if mins is None:
		mins = ys.min(axis=0)
	else:
		mins = mins.cpu().numpy()
	ymins = mins
	if maxs is None:
		maxs = ys.max(axis=0)
	else:
		maxs = maxs.cpu().numpy()
	ymaxs = maxs
	dys = ymaxs - ymins
	ymins -= dys * 0.05  # add 5% padding below and above
	ymaxs += dys * 0.05
	
	#     ymaxs[1], ymins[1] = ymins[1], ymaxs[1]  # reverse axis 1 to have less crossings
	dys = ymaxs - ymins
	
	# transform all data to be compatible with the main axis
	zs = np.zeros_like(ys)
	zs[:, 0] = ys[:, 0]
	zs[:, 1:] = (ys[:, 1:] - ymins[1:]) / dys[1:] * dys[0] + ymins[0]
	
	if figax is None:
		figax = plt.subplots(figsize=figsize)
	fig, host = figax
	
	axes = [host] + [host.twinx() for i in range(ys.shape[1] - 1)]
	for i, ax in enumerate(axes):
		ax.set_ylim(ymins[i], ymaxs[i])
		ax.spines['top'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		if ax != host:
			ax.spines['left'].set_visible(False)
			ax.yaxis.set_ticks_position('right')
			ax.spines["right"].set_position(("axes", i / (ys.shape[1] - 1)))
	
	host.set_xlim(0, ys.shape[1] - 1)
	host.set_xticks(range(ys.shape[1]))
	host.set_xticklabels(ynames, fontsize=14)
	host.tick_params(axis='x', which='major', pad=7)
	host.spines['right'].set_visible(False)
	host.xaxis.tick_top()
	#     host.set_title('Parallel Coordinates Plot — Iris', fontsize=18, pad=12)
	
	#     colors = plt.cm.Set2.colors
	legend_handles = {}
	for j in range(ys.shape[0]):
		# create bezier curves
		verts = list(zip([x for x in np.linspace(0, len(ys) - 1, len(ys) * 3 - 2, endpoint=True)],
						 np.repeat(zs[j, :], 3)[1:-1]))
		codes = [Path.MOVETO] + [Path.CURVE4 for _ in range(len(verts) - 1)]
		path = Path(verts, codes)
		
		if categories is None:
			style = default_style
		else:
			cls = categories[j]
			if cat_names is not None:
				cls = cat_names[cls]
			style = cat_styles[cls]
		
		patch = patches.PathPatch(path, **style)  # facecolor='none', lw=2, alpha=0.7, edgecolor=colors[iris.target[j]])
		
		host.add_patch(patch)
		
		if categories is not None:
			legend_handles[cls] = patch
	
	if include_legend:
		host.legend([legend_handles[c] for c in classes], classes,
					loc='lower center', bbox_to_anchor=(0.5, -0.18),
					ncol=len(classes), fancybox=True, shadow=True)
	
	return fig, host

def remove_keys(data, remove=[]):
	remove = set(remove)
	keys = set(data.keys())
	remove = remove.intersection(keys)
	for r in remove:
		del data[r]


