
import sys, os

import numpy as np

from datetime import datetime
from datetime import timedelta

import yfinance as yf
# from yahoofinancials import YahooFinancials

from humpack import tdict, Key_Table

def get_table(tks, pbar=None):
	tbl = Key_Table(_type=Stock, _get_key=lambda s: s.name)
	for name in (tks if pbar is None else pbar(tks)):
		tbl.new(name)
	return tbl

START, END = None, None
def get_start_end(interval=365, start=None):
	now = datetime.today()
	if start is None:
		start = interval
	s = now - timedelta(days=int(start))
	e = s + timedelta(days=int(interval))
	# global START, END
	# START, END = s, e
	return s, e

def sample_time(batch=10, interval=100, max_hist=3*365, overlap=True):

	# options = (max_hist - interval) if overlap else ((max_hist+interval-1) // interval)
	options = (max_hist - interval) if overlap else (max_hist // interval)

	if not overlap:
		batch = min(batch, options)

	idx = np.random.choice(options, size=(batch,), replace=overlap)

	return idx, idx+interval

	# tins = []
	#
	# for x in idx:
	# 	tins.append(get_start_end(interval=interval, start=x))
	#
	# return tins





def get_startdate(months):
	return datetime.today() - timedelta(days=int(365/12*months))
def get_ticker(ticker):
	return yf.Ticker(ticker)

class Stock(tdict):
	def __init__(self, name):
		self.name = name
		self.ticker = yf.Ticker(name)
		self.hist = None
		self.info = None
	
	def get_history(self, *args, **kwargs):
		return self.ticker.history(*args, **kwargs)
		if self.hist is None:
			self.hist = self.ticker.history(*args, **kwargs)
		return self.hist
	
	def get_closes(self, *args, p=True, **kwargs):
		hist = self.get_history(*args, **kwargs)
		data = hist.to_numpy()[:, 3]
		if p:
			data /= data[0]
			data -= 1
			data *= 100
		return data
	
	#     def get_recommendations(self):
	#         return self.ticker.recommendations
	
	def get_info(self):
		if self.info is None:
			self.info = self.ticker.info
		return self.info



