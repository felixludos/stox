
import traceback
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from . import yahoo

class Criterion(nn.Module):
	
	def __init__(self, wt=1.):
		super().__init__()
		self.wt = wt
	
	
	def prepare(self, tickers):
		pass
	
	
	def quality(self, tickers):
		pass
	
	
	def loss(self, q):
		return 0.
	
	
	def forward(self, q):
		return self.wt * self.loss(q)


class MultiCriterion(Criterion):
	def __init__(self, criteria=[], **kwargs):
		super().__init__(**kwargs)
		self.criteria = criteria
		
	def prepare(self, tickers):
		for criterion in self.criteria:
			criterion.prepare(tickers)
		
	def loss(self, q):
		return sum(criterion(q) for criterion in self.criteria)



class PortfolioMatching(Criterion):
	def __init__(self, portfolio, key=None, normalize=True, measure=None, **kwargs):
		super().__init__(**kwargs)
		if isinstance(portfolio, str):
			portfolio = yahoo.load_portfolio(portfolio)['portfolio']
		# if measure is None:
		# 	measure = nn.MSELoss()
		self.measure = measure
		self.portfolio = portfolio
		self.key = key
		self.normalize = normalize
		
	
	def prepare(self, tickers):
		existing = [tk.ticker for tk in tickers]
		relevant = {tk: r for tk, r in self.portfolio.items() if tk in existing}
		self.best_case = sum(relevant.values())
		self.best = torch.as_tensor([relevant.get(tk, 0.) for tk in existing]).float()
		if self.normalize:
			self.best /= self.best.sum()
		
		num = 1
		groups = None
		idents = {}
		if self.key is not None:
			idents = {tk.ticker: self.key(tk) for tk in tickers}
			groups = {g: i for i, g in enumerate(set(idents.values())) if g is not None}
			num = len(groups)
		
		self.N = len(existing)
		self.param = torch.zeros(self.N, num).float()
		
		for tk, row in zip(existing, self.param):
			if groups is None:
				row[0] = 1.
			elif tk in idents and idents[tk] in groups:
				row[groups[idents[tk]]] = 1.
		
		self.target = self.best.view(1, -1) @ self.param
		
	
	def loss(self, q):
		if self.key is None:
			res = q
			target = self.best
		else:
			res = q.view(-1, self.N) @ self.param
			target = self.target
		if self.measure is None:
			return -res.sub(target).abs().sum()
		return -self.measure(res, target)


class GroupScoring(Criterion):
	def __init__(self, groups, key, standardize=True, **kwargs):
		super().__init__(**kwargs)
		self.groups = groups
		self.key = key
		self.standardize = standardize
	
	def apply(self, tickers):
		return [self.key(tk) for tk in tickers]
	
	def prepare(self, tickers):
		existing = self.apply(tickers)
		vals = torch.as_tensor([self.groups.get(v, 0.) for v in existing]).float()
		if self.standardize:
			vals /= vals.abs().sum()
		
		self.param = vals
	
	def loss(self, q):
		return q @ self.param


class GroupMatching(Criterion):
	def __init__(self, groups, key, aliases={}, as_logits=True, **kwargs):
		super().__init__(**kwargs)
		self.aliases = aliases
		self.groups_raw = groups
		
		gnames, wts = zip(*groups.items())
		wts = torch.as_tensor(wts).float()
		as_logits = as_logits or wts.lt(0.).any()
		wts = F.softmax(wts,dim=0) if as_logits else F.normalize(wts, p=1,dim=0)
		self.groups = dict(zip(gnames, wts.tolist()))
		self.indices = {name:idx for idx, name in enumerate(gnames)}
		self.target = wts
		
		self.key = key
		# self.standardize = standardize
		self.as_logits = as_logits
	
	def apply(self, tickers):
		return [self.key(tk) for tk in tickers]
	
	def prepare(self, tickers):
		existing = self.apply(tickers)
		self.param = torch.zeros(len(existing), len(self.indices))
		for i, v in enumerate(existing):
			v = self.aliases.get(v,v)
			if v in self.indices:
				self.param[i,self.indices[v]] = 1.# self.groups[v]
				
	def loss(self, q):
		vals = q @ self.param
		return -vals.sub(self.target).pow(2).sum().sqrt()


class ManualReqs(Criterion):
	def __init__(self, reqs, p=2, **kwargs):
		super().__init__(**kwargs)
		self.reqs = reqs
		self.p = p
	
	def prepare(self, tickers):
		self.param = torch.as_tensor([self.reqs.get(tk, 0.) for tk in tickers])
		
	def loss(self, q):
		return -F.relu(self.param - q).pow(self.p).sum()


class FeatureVariance(Criterion):
	def __init__(self, feature, normalize=False, **kwargs):
		super().__init__(**kwargs)
		self.feature = feature
		self.normalize = normalize
		
	def prepare(self, tickers):
		vals = np.array([(float('nan') if val is None else val) for val in map(self.feature, tickers)])
		good = np.isfinite(vals)
		assert good.sum() > 1
		
		pts = vals[good]
		
		# if self.normalize:
		# 	pts /= np.abs(pts).sum()
		# pts -= pts.mean()
		# pts = np.abs(pts)
		self.param = torch.zeros(len(vals))
		self.sel = torch.from_numpy(good).bool()
		self.param[self.sel] = torch.from_numpy(pts).float()

	def loss(self, q):
		mu = q @ self.param / q[self.sel].sum()
		return q @ (self.param - mu).pow(2) / q[self.sel].sum()



class ClipWeight(Criterion):
	def __init__(self, limit, p=2, **kwargs):
		super().__init__(**kwargs)
		self.limit = limit
		self.p = p

	
	def loss(self, q):
		return -F.relu(q-self.limit).pow(self.p).sum()



class UnitShares(Criterion):
	def __init__(self, capital, p=2, **kwargs):
		super().__init__(**kwargs)
		self.capital = capital
		self.p = p
	
	def prepare(self, tickers):
		vals = np.array([(float('nan') if val is None else val)
		                 for val in map(lambda tk: tk.info.get('currentPrice'), tickers)])
		good = np.isfinite(vals)
		assert good.sum() > 1
		
		pts = vals[good]
		
		# if self.normalize:
		# 	pts /= np.abs(pts).sum()
		# pts -= pts.mean()
		# pts = np.abs(pts)
		self.param = torch.zeros(len(vals))
		self.sel = torch.from_numpy(good).bool()
		self.param[self.sel] = self.capital / torch.from_numpy(pts).float()
	
	def loss(self, q):
		m = self.param @ q
		m = m - (m > 0.5).float()
		return -m.pow(2).sum().div(2)



class FeatureExtractor(Criterion):
	def __init__(self, features, normalize=True, standardize=True, use_percentile=False, **kwargs):
		super().__init__(**kwargs)
		self.use_percentile = use_percentile
		
		wts = []
		funcs = []
		for feature in features:
			w = 1
			if isinstance(feature, tuple):
				w, feature = feature
			funcs.append(feature)
			wts.append(w)

		self.wts = torch.as_tensor(wts).float()
		if normalize:
			self.wts /= self.wts.abs().sum()
		self.features = funcs
		self.standardize = standardize


	def prepare(self, tickers):
		dat = []
		for tk in tickers:
			fs = []
			for i, feature in enumerate(self.features):
				v = 0.
				try:
					v = feature(tk)
				except:
					print(tk.ticker, i)
					traceback.print_exc()
				# if v is None or v-v != 0:
				# 	v = 0.
				fs.append(v)
			dat.append(fs)
		dat = torch.as_tensor(dat).float()
		full_costs = dat * self.wts.view(1, -1)
		
		stands = []
		for row in full_costs.t():
			good = row[row.isnan().logical_not()]
			if len(good):
				mn, mx = good.min(), good.max()
				stands.append(row.sub(mn).div(mx - mn))
			else:
				stands.append(row)
		stands = torch.stack(stands).t()
		self.feat_dats = dat
		self.percentile_dats = stands
		
		wts = self.wts.abs().view(-1,1) if self.use_percentile else self.wts.view(-1, 1)
		costs = stands.clone() if self.use_percentile else dat.clone()
		costs[costs.isnan()] = 0.
		
		self.costs = costs @ wts
		self.costs = self.costs.squeeze()
		if self.standardize:
			self.costs /= self.costs.abs().sum()
		

	def loss(self, q):
		return self.costs @ q





