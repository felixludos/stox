
weights = {
	'companies': 0.25,
	
	'us-index': 0.25,
	'china-index': 0.1,
	'eu-index': 0.05,
	'ex-us': 0.05,
	
	'volatile': 0.1,
	
	'bonds': 0.1,
	'commodities': 0.1,
}

nations = {
	'China': ['0700.HK', 'BIDU', 'BABA'],
	'US': ['MSFT', 'AMZN', 'TSLA', 'AMD', 'NVDA', 'GOOG', 'FB', 'PYPL', 'NFLX', 'DIS'],
	'Japan': ['NTDOY', 'SNE'],
}

sectors = {
	'Consumer Discretionary': ['SNE', ],
	
}

stocks = {
	'SNE': {
		'nation': 'Japan',
		'sector': 'Consumer Discretionary',
		'dividends': 0.56,
	},
	'NTDOY':{
		'nation': 'Japan',
		'sector': 'Communication Services',
		'dividends': 0,
	},
	
	'0700.HK':{
		'nation': 'China',
		'sector': 'Communication Services',
	},
	'BIDU':{
		'sector': 'Communication Services',
		'nation': 'China',
	},
	'BABA':{
		'sector': 'Consumer Discretionary',
		'nation': 'China',
	},
	
	'MSFT':{
		'nation': 'US',
		'sector': 'Information Technology',
		'dividends': 0.95,
	},
	'AMZN':{
		'nation': 'US',
		'sector': 'Consumer Discretionary',
	},
	'TSLA': {
		'nation': 'US',
		'sector': 'Consumer Discretionary',
	},
	'AMD': {
		'nation': 'US',
		'sector': 'Information Technology',
	},
	'NVDA': {
		'nation': 'US',
		'sector': 'Information Technology',
	},
	'GOOG': {
		'nation': 'US',
		'sector': 'Communication Services',
	},
	'FB': {
		'nation': 'US',
		'sector': 'Communication Services',
	},
	'PYPL': {
		'nation': 'US',
		'sector': 'Information Technology',
	},
	'NFLX': {
		'nation': 'US',
		'sector': 'Communication Services',
	},
	'DIS': {
		'nation': 'US',
		'sector': 'Communication Services',
	},
}

strategy = {
	
	'companies': { # 0.25
		'MSFT': 0.03,
		'AMZN': 0.03,
		'TSLA': 0.03,
		'AMD': 0.02,
		'NVDA': 0.02,
		'BABA': 0.03,
		'0700.HK': 0.03,
		'GOOG': 0.01,
		'BIDU': 0.01,
		'SNE': 0.005,
		'NTDOY': 0.01,
		'FB': 0.005,
		'PYPL': 0.01,
		'NFLX': 0.005,
		'DIS': 0.005,
	},
	
	'us-general' :{ # 0.12
		'FZROX': 0.06,
		'FSMAX': 0.03,
		'FZIPX': 0.03,
	},
	
	'us-tech' :{ # 0.12
		'VONG': 0.03,
		'XITK': 0.02,
		'SOCL': 0.01,
		'ESPO': 0.015,
		'CIBR': 0.015,
		'SKYY': 0.01,
		# 'LIT': 0.005,
		'IBB': 0.02,
	},
	
	'us-healthcare' :{ # 0.01
		'FHLC': 0.01,
	},
	
	'us-energy' :{ # 0.04
		'PHO': 0.01,
		'ACES': 0.02,
		'ICLN': 0.01,
	},
	
	'us-other' :{ # 0.01
		'FIDU': 0.005,
		'FNCL': 0.005,
	},
	
	'china' :{ # 0.12
		'ASHR': 0.045,
		'CNYA': 0.035,
		'KWEB': 0.02,
		'MCHI': 0.01,
	},
	
	'euj' :{ # 0.07
		'FSPSX': 0.035,
		# 'FLGR': 0.015,
		'VGK': 0.01,
		'EWG': 0.005,
		'FLJP': 0.015,
		'EWY': 0.005,
	},
	
	'ex-us' :{ # 0.07
		'FSGGX': 0.04,
		# 'XCEM': 0.03,
		'EMXC': 0.03,
	},
	
	'bonds-treasury' :{ # 0.09
		'FIPDX': 0.01,
		'VGLT': 0.02,
		'FUAMX': 0.025,
		'SCHO': 0.02,
		'MINT': 0.005,
		'IGOV': 0.01,
	},
	
	'bonds-corporate' :{ # 0.06
		'VCLT': 0.02,
		'AGG': 0.01,
		'VCSH': 0.01,
		'LQD': 0.01,
		'IAGG': 0.01,
	},
	
	'commodities' :{ # 0.05
		'IAU': 0.05,
	},
}

etfs = {
	'FZROX': {
		'expenses': 0.,
		'nations': {'US':99.98},
		'sectors': {'Information Technology': 25.41, 'Health Care': 15.25, 'Financials': 10.88, 'Consumer Discretionary': 10.86, 'Communication Services': 10.04, 'Industrials': 8.6, 'Consumer Staples': 6.45, 'Real Estate': 3.57, 'Utilities': 3.14, 'Materials': 2.72, 'Energy': 2.7, 'Multi Sector': 0.37},
		'holdings': {'ADBE': 0.63, 'XOM': 0.64, 'BAC': 0.65, 'CSCO': 0.68, 'MRK': 0.69, 'DIS': 0.71, 'PFE': 0.71, 'NVDA': 0.73, 'T': 0.76, 'VZ': 0.79, 'MA': 0.89, 'HD': 0.91, 'INTC': 0.92, 'PG': 0.97, 'UNH': 0.97, 'JPM': 1.02, 'V': 1.12, 'BRK.B': 1.21, 'JNJ': 1.31, 'GOOGL': 1.43, 'GOOG': 1.44, 'FB': 1.81, 'AMZN': 3.41, 'AAPL': 4.45, 'MSFT': 4.68}},
	'FSMAX': {
		'expenses': 0.036,
		'sectors': {'Information Technology': 20.95, 'Health Care': 15.94, 'Financials': 14.51, 'Consumer Discretionary': 12.7, 'Industrials': 12.41, 'Real Estate': 7.63, 'Communication Services': 4.83, 'Materials': 3.74, 'Consumer Staples': 2.76, 'Utilities': 2.57, 'Energy': 1.52, 'Multi Sector': 0.44},
		'nations': {'US': 99.97},
		'holdings':{'COUP': 0.31, 'SNAP': 0.32, 'TYL': 0.32, 'KKR': 0.33, 'ALNY': 0.33, 'TRU': 0.35, 'DOCU': 0.38, 'SGEN': 0.39, 'MRNA': 0.4, 'BMRN': 0.42, 'ICA': 0.43, 'RNG': 0.45, 'LBRDK': 0.46, 'MRVL': 0.47, 'OKTA': 0.48, 'PANW': 0.5, 'TWLO': 0.54, 'CSGP': 0.56, 'SQ': 0.6, 'SPLK': 0.62, 'VEEV': 0.63, 'WDAY': 0.65, 'LULU': 0.78, 'BX': 0.82, 'TSLA': 2.59}
	},
	'FZIPX': {
		'expenses': 0.,
		'sectors': {'Information Technology': 16.34, 'Health Care': 16.29, 'Industrials': 15.0, 'Financials': 13.68, 'Consumer Discretionary': 12.68, 'Real Estate': 7.84, 'Materials': 5.13, 'Communication Services': 3.56, 'Consumer Staples': 3.55, 'Utilities': 2.87, 'Energy': 2.44, 'Multi Sector': 0.66},
		'nations': {'US': 99.95, 'Canada': 0.03},
		'holdings': {'HZNP': 0.25, 'CABO': 0.25, 'IR': 0.26, 'CGNX': 0.26, 'RPM': 0.26, 'AAP': 0.26, 'NDSN': 0.26, 'ETSY': 0.26, 'ZEN': 0.26, 'PKG': 0.26, 'ETFC': 0.27, 'JBHT': 0.27, 'ABMD': 0.27, 'TECH': 0.27, 'BIO': 0.28, 'CHRW': 0.29, 'SRPT': 0.29, 'POOL': 0.29, 'W': 0.3, 'MASI': 0.31, 'MOH': 0.31, 'NBIX': 0.31, 'CTLT': 0.32, 'TDOC': 0.34, 'MRNA': 0.49}
	},
	
	'VONG': {
		'expenses': 0.08,
		'sectors': {'Information Technology': 43.49, 'Consumer Discretionary': 16.41, 'Health Care': 14.42, 'Communication Services': 11.65, 'Consumer Staples': 4.71, 'Industrials': 4.38, 'Financials': 2.08, 'Real Estate': 1.99, 'Materials': 0.82, 'Energy': 0.07, 'Utilities': 0.02},
		'nations': {'US': 98.28, 'Ireland': 0.91, 'UK': 0.51, 'Luxembourg': 0.24, 'Israel': 0.05, 'China': 0.01},
		'holdings': {'TSLA': 0.76, 'KO': 0.77, 'AMGN': 0.78, 'ACN': 0.81, 'LLY': 0.82, 'COST': 0.85, 'ABBV': 0.86, 'CRM': 0.92, 'PEP': 0.97, 'HD': 0.97, 'NFLX': 1.11, 'PYPL': 1.15, 'ADBE': 1.17, 'MRK': 1.23, 'CSCO': 1.29, 'NVDA': 1.3, 'MA': 1.68, 'UNH': 1.81, 'V': 2.1, 'GOOGL': 2.7, 'GOOG': 2.7, 'FB': 3.38, 'AMZN': 6.42, 'AAPL': 8.24, 'MSFT': 8.72}
	},
	'XITK': {
		'expenses': 0.45,
		'sectors': {'Information Technology': 64.6, 'Communication Services': 30.69, 'Health Care': 1.97, 'Consumer Discretionary': 1.41, 'Financials': 0.79, 'Industrials': 0.61},
		'nations': {'US': 78.18, 'China': 12.71, 'Singapore': 2.35, 'Israel': 2.02, 'UK': 1.87, 'Luxembourg': 1.36, 'Russia': 0.85, 'France': 0.67},
		'holdings': {'NFLX': 1.18, 'BL': 1.27, 'AYX': 1.28, 'VEEV': 1.28, 'APPF': 1.28, 'TEAM': 1.32, 'NVDA': 1.35, 'SEDG': 1.35, 'COUP': 1.39, 'WORK': 1.4, 'GLUU': 1.42, 'TWOU': 1.43, 'OKTA': 1.44, 'IPHI': 1.45, 'CRWD': 1.52, 'EVBG': 1.55, 'MDB': 1.55, 'BILI': 1.55, 'WIX': 1.59, 'DOCU': 1.62, 'SHOP': 1.69, 'TWLO': 1.73, 'ZS': 1.83, 'SE': 1.85, 'ZM': 2.42}
	},
	'SOCL': {
		'expenses': 0.65,
		'sectors': {'Communication Services': 98.15, 'Consumer Discretionary': 0.23},
		'nations': {'US': 43.22, 'China': 24.72, 'Korea': 13.55, 'Luxembourg': 6.37, 'Russia': 5.61, 'Japan': 4.85, 'Germany': 1.56, 'Taiwan': 0.11},
		'holdings':{'SINA': 0.7, 'YY': 0.77, 'LNNFF': 0.98, 'MOMO': 1.0, 'KKKUF': 1.13, 'MLRYY': 1.17, 'UDIRF': 1.51, 'MTCH': 1.75, 'BILI': 2.06, 'TME': 2.54, 'PINS': 2.95, 'ZNGA': 2.96, '035720.KS': 3.35, 'NEXOF': 3.41, 'BIDU': 4.14, 'YNDX': 4.18, 'NTES': 4.22, 'GOOGL': 4.55, 'IAC': 4.95, 'SPOT': 5.18, 'SNAP': 6.91, 'NHNCF': 7.94, '0700.HK': 8.48, 'TWTR': 8.55, 'FB': 10.74}
	},
	'ESPO': {
		'expenses': 0.55,
		'sectors': {'Communication Services': 78.02, 'Information Technology': 18.53, 'Consumer Discretionary': 3.69},
		'nations': {'US': 34.34, 'China': 21.36, 'Japan': 20.62, 'Korea': 7.27, 'Singapore': 5.25, 'Poland': 3.85, 'France': 3.55, 'Taiwan': 2.16, 'Sweden': 1.61},
		'holdings':{'DNACF': 0.82, '263750.KQ': 0.89, 'KSFTF': 1.41, '251270.KS': 1.52, 'EMBRACB': 1.58, 'CCOEF': 1.95, 'KNAMF': 2.08, '2377.TW': 2.12, 'SQNXF': 2.28, 'BILI': 2.97, 'UBSFF': 3.8, 'NCBDF': 3.82, 'TTWO': 4.14, '036570.KS': 4.14, 'NTES': 4.75, 'NEXOF': 4.87, 'ZNGA': 4.95, 'EA': 5.37, 'OTGLF': 5.39, 'NTDOF': 5.55, 'SE': 6.02, 'ATVI': 6.34, 'AMD': 6.63, '0700.HK': 7.14, 'NVDA': 9.27}
	},
	'CIBR': {
		'expenses':0.6,
		'sectors': {'Information Technology': 94.77, 'Industrials': 4.82},
		'nations': {'US': 85.29, 'UK': 5.9, 'Israel': 3.39, 'Japan': 2.66, 'France': 1.83, 'Korea': 0.49},
		'holdings':{'RPD': 1.59, 'THLEF': 1.95, 'SAIC': 1.96, 'BAESF': 2.01, 'QLYS': 2.23, 'FEYE': 2.4, 'TMICF': 2.44, 'CYBR': 2.53, 'LDOS': 2.62, 'CHKP': 2.69, 'PFPT': 2.78, 'BAH': 2.85, 'JNPR': 2.92, 'VRSN': 2.94, 'FFIV': 3.08, 'AKAM': 3.12, 'VMW': 3.31, 'FTNT': 3.48, 'OKTA': 3.89, 'ZS': 4.81, 'AVGO': 5.45, 'CSCO': 6.11, 'SPLK': 6.43, 'PANW': 6.5, 'CRWD': 7.51}
	},
	'SKYY': {
		'expenses': 0.6,
		'sectors': {'Information Technology': 82.55, 'Consumer Discretionary': 9.27, 'Communication Services': 6.88, 'Health Care': 1.36},
		'nations': {'US': 90.93, 'China': 4.52, 'UK': 2.49, 'Germany': 1.44, 'Canada': 0.62},
		'holdings':{'NTAP': 1.64, 'IBM': 1.65, 'NTNX': 1.73, 'CRM': 1.76, 'HUBS': 1.91, 'ADBE': 1.93, 'PSTG': 1.98, 'NOW': 2.04, 'SPLK': 2.17, 'TEAM': 2.2, 'CTL': 2.33, 'FIVN': 2.45, 'CSCO': 2.74, 'AKAM': 2.8, 'SHOP': 2.81, 'BABA': 2.86, 'TWLO': 3.01, 'CTXS': 3.28, 'ANET': 3.46, 'GOOGL': 3.68, 'ORCL': 3.74, 'MSFT': 3.89, 'MDB': 4.36, 'AMZN': 4.45, 'VMW': 4.46}
	},
	'LIT': {
		'expenses': 0.75,
		'sectors': {'Materials': 42.86, 'Industrials': 20.77, 'Consumer Discretionary': 18.64, 'Information Technology': 17.33},
		'nations': {'China': 50.33, 'US': 20.01, 'Korea': 11.26, 'Japan': 5.48, 'Australia': 3.79, 'Chile': 3.14, 'Taiwan': 2.39, 'Switzerland': 2.08, 'Netherlands': 0.6, 'Canada': 0.25, 'Hong Kong': 0.15, 'Germany': 0.12},
		'holdings':{'AZZVF': 0.36, 'ULBI': 0.37, 'GSCCF': 0.4, 'ASL.DE': 0.47, 'WSPCF': 0.59, '8137.HK': 0.59, 'LAC': 0.69, '082920.KQ': 0.85, 'GALXF': 0.95, '066970.KQ': 1.27, 'PILBF': 1.28, 'OROCF': 1.39, '3211.TW': 1.67, 'LTHM': 3.97, 'ENS': 4.0, 'GYUAF': 4.27, 'VARGF': 4.4, 'PCRFF': 4.48, 'BYDDF': 4.68, '6121.TW': 4.87, 'LGCLF': 5.04, '005930.KS': 6.41, 'SQM': 11.71, 'TSLA': 13.12, 'ALB': 19.6}
	},
	'IBB': {
		'expenses': 0.47,
		'sectors': {'Health Care': 99.79, 'Materials': 0.08},
		'nations': {'US': 92.63, 'China': 1.78, 'France': 1.19, 'UK': 0.96, 'Netherlands': 0.85, 'Denmark': 0.79, 'Switzerland': 0.63, 'Ireland': 0.3, 'Spain': 0.25, 'Canada': 0.18, 'Israel': 0.18, 'Hong Kong': 0.15, 'Singapore': 0.04},
		'holdings':{'NVCR': 0.73, 'BGNE': 0.76, 'IMMU': 0.78, 'EXEL': 0.82, 'ACAD': 0.84, 'IONS': 0.86, 'GH': 0.92, 'MYL': 0.96, 'HZNP': 1.05, 'TECH': 1.1, 'SNY': 1.11, 'NBIX': 1.25, 'SRPT': 1.29, 'ALNY': 1.65, 'BMRN': 2.08, 'INCY': 2.4, 'MRNA': 2.46, 'ALXN': 2.88, 'SGEN': 2.94, 'ILMN': 4.61, 'BIIB': 5.71, 'REGN': 7.08, 'GILD': 7.56, 'AMGN': 7.75, 'VRTX': 7.97}
	},
	
	'FHLC': {
		'expenses': 0.08,
		'sectors': {'Health Care': 99.42},
		'nations': {'US': 99.0, 'UK': 0.19, 'Switzerland': 0.1, 'Netherlands': 0.04, 'Canada': 0.03, 'Ireland': 0.01, 'Japan': 0.01, 'Puerto Rico': 0.01},
		'holdings': {'BSX': 1.17, 'ILMN': 1.18, 'HUM': 1.2, 'BIIB': 1.22, 'SYK': 1.46, 'ZTS': 1.47, 'ISRG': 1.48, 'BDX': 1.48, 'CI': 1.63, 'VRTX': 1.64, 'ANTM': 1.65, 'CVS': 1.89, 'GILD': 2.18, 'DHR': 2.3, 'LLY': 2.92, 'MDT': 2.92, 'AMGN': 3.02, 'TMO': 3.09, 'BMY': 3.09, 'ABBV': 3.61, 'ABT': 3.71, 'MRK': 4.54, 'PFE': 4.67, 'UNH': 6.38, 'JNJ': 8.65}
	},
	
	'PHO': {
		'expenses':0.6,
		'sectors': {'Industrials': 49.05, 'Utilities': 22.54, 'Health Care': 16.45, 'Materials': 7.59, 'Information Technology': 4.39},
		'nations': {'US': 97.68, 'Brazil': 2.2, 'UK':.13},
		'holdings':{'MWA': 1.11, 'FELE': 1.33, 'BMI': 1.49, 'WTS': 1.5, 'CWT': 1.64, 'AQUA': 1.78, 'VMI': 1.8, 'SBS': 1.93, 'WMS': 1.95, 'ITRI': 2.33, 'AWR': 2.76, 'TTEK': 2.93, 'RXN': 3.19, 'HDS': 3.25, 'XYL': 3.34, 'PNR': 3.88, 'TTC': 3.89, 'WTRG': 3.97, 'IEX': 4.21, 'AOS': 4.69, 'WAT': 8.01, 'AWK': 8.02, 'ROP': 8.74, 'DHR': 9.0, 'ECL': 9.2}
	},
	'ACES': {
		'expenses': 0.65,
		'sectors': {'Utilities': 29.88, 'Industrials': 26.64, 'Information Technology': 24.21, 'Consumer Discretionary': 7.85, 'Financials': 3.86, 'Energy': 3.0},
		'nations': {'US': 70.93, 'Canada': 27.70, 'France': 1.36},
		'holdings':{'SPWR': 1.27, 'TPIC': 1.44, 'EVA': 1.47, 'CVA': 2.21, 'REGI': 2.27, 'TRSWF': 2.3, 'PLUG': 2.56, 'RUN': 2.9, 'TERP': 3.37, 'CWEN': 3.61, 'BLDP': 3.64, 'INGXF': 3.69, 'HASI': 3.93, 'BRLXF': 3.99, 'AYI': 4.37, 'NEP': 4.56, 'ITRI': 4.63, 'BEP': 4.75, 'OLED': 4.91, 'NPIFF': 5.08, 'ORA': 5.36, 'FSLR': 5.61, 'ENPH': 5.73, 'TSLA': 6.2, 'CREE': 6.27}
	},
	'ICLN': {
		'expenses': 0.46,
		'sectors': {'Utilities': 48.85, 'Information Technology': 28.12, 'Industrials': 20.66, 'Energy': 1.93},
		'nations': {'US': 26.0, 'Canada': 12.68, 'China': 9.57, 'New Zealand': 7.3, 'Israel': 7.25, 'Germany': 6.99, 'Brazil': 6.81, 'France': 4.66, 'Denmark': 4.25, 'UK': 3.71, 'Austria': 3.57, 'Norway': 3.37, 'Spain': 1.81, 'Italy': 1.59},
		'holdings':{'FKR.MI': 1.69, 'XJNGF': 1.69, 'CSIQ': 2.1, 'REGI': 2.68, 'CAP.DE': 2.82, 'NEOEN.PA': 2.84, 'ELP': 2.92, 'PLUG': 3.01, 'RUN': 3.15, 'TERP': 3.54, 'BRLXF': 3.72, 'AY': 3.74, 'INGXF': 3.77, 'STECF': 3.79, 'OEZVF': 3.9, 'GCTAF': 4.2, 'MDDNF': 4.21, 'COENF': 4.24, 'ORA': 4.34, 'VWSYF': 4.39, 'XNYIF': 4.51, 'CIG': 4.52, 'FSLR': 4.65, 'SEDG': 5.95, 'ENPH': 6.18}
	},
	
	'FIDU': {
		'expenses': 0.08,
		'sectors': {'Industrials': 99.55},
		'nations': {'US':97.21, 'Ireland':1.04, 'Canada':.99, 'UK':.23},
		'holdings':{'ROK': 0.97, 'PCAR': 0.99, 'INFO': 1.02, 'VRSK': 1.04, 'FDX': 1.25, 'ETN': 1.36, 'GD': 1.4, 'EMR': 1.44, 'ROP': 1.59, 'LHX': 1.71, 'WM': 1.75, 'DE': 1.76, 'NSC': 1.8, 'CSX': 2.05, 'NOC': 2.08, 'ITW': 2.15, 'GE': 2.22, 'CAT': 2.57, 'UPS': 2.71, 'BA': 3.02, 'MMM': 3.48, 'RTX': 3.78, 'LMT': 3.82, 'HON': 4.03, 'UNP': 4.56}
	},
	'FNCL': {
		'expenses': 0.08,
		'sectors': {'Financials': 97.62},
		'nations': {'US': 93.93, 'UK':3.64, 'Mexico': .11, 'China': 0.01},
		'holdings': {'BK': 0.97, 'COF': 0.99, 'ALL': 0.99, 'BX': 1.17, 'SCHW': 1.3, 'MCO': 1.42, 'PGR': 1.42, 'AON': 1.45, 'TFC': 1.55, 'PNC': 1.57, 'USB': 1.65, 'MS': 1.68, 'MMC': 1.68, 'ICE': 1.7, 'CB': 1.73, 'GS': 1.96, 'CME': 2.05, 'AXP': 2.07, 'SPGI': 2.49, 'BLK': 2.52, 'C': 3.28, 'WFC': 3.33, 'BAC': 6.46, 'BRK.B': 7.65, 'JPM': 9.57}
	},
	
	'ASHR': {
		'expenses': 0.65,
		'sectors': {'Financials': 29.3, 'Consumer Staples': 15.03, 'Information Technology': 13.21, 'Industrials': 10.5, 'Health Care': 8.52, 'Consumer Discretionary': 8.46, 'Materials': 5.41, 'Real Estate': 3.75, 'Communication Services': 2.27, 'Utilities': 1.83, 'Energy': 1.39},
		'nations': {'China': 96.86, 'Hong Kong': 1.85, 'UK': 0.85, 'Taiwan': 0.29, 'US': 0.09, 'France': 0.06},
		'holdings':{'601318.SS': 5.28, '600519.SS': 5.0, '600036.SS': 2.37, '600276.SS': 2.34, '000858.SZ': 2.27, '000333.SZ': 2.0, '000651.SZ': 1.86, '002475.SZ': 1.47, '600030.SS': 1.4, '601166.SS': 1.34}
	},
	'CNYA': {
		'expenses': 0.6,
		'sectors': {'Financials': 22.62, 'Consumer Staples': 16.32, 'Information Technology': 15.05, 'Industrials': 11.89, 'Health Care': 10.85, 'Materials': 6.63, 'Consumer Discretionary': 5.84, 'Real Estate': 3.72, 'Communication Services': 2.58, 'Utilities': 2.22, 'Energy': 1.63},
		'nations':{'China': 96.31, 'Hong Kong': 1.48, 'UK': 1.03, 'Taiwan': 0.36, 'France': 0.12, 'Denmark': 0.11, 'Switzerland': 0.09},
		'holdings':{'600519.SS': 5.75, '601318.SS': 2.49, '600036.SS': 2.2, '000858.SZ': 2.12, 'ICSUAGD': 1.43, '600276.SS': 1.4, '300750.SZ': 1.22, '600900.SS': 1.12, '002475.SZ': 1.05, '601166.SS': 1.03}
	},
	'KWEB': {
		'expenses': 0.76,
		'sectors': {'Consumer Discretionary': 36.75, 'Communication Services': 35.75, 'Health Care': 6.0, 'Information Technology': 3.59, 'Financials': 2.27, 'Industrials': 0.89},
		'nations': {'China': 94.39, 'US':5.17, 'Hong Kong':0.43},
		'holdings': {'1060.HK': 0.85, '780.HK': 0.85, 'JOBS': 1.04, 'WB': 1.11, 'SINA': 1.13, '772.HK': 1.16, 'KSFTF': 1.29, 'GSX': 1.56, 'MOMO': 1.73, 'YY': 2.1, 'TME': 2.22, 'ATHM': 2.28, 'WUBA': 2.53, 'IQ': 2.55, 'TCOM': 2.84, 'BILI': 3.74, 'VIPS': 4.32, 'TAL': 4.42, 'NTES': 4.52, 'BIDU': 5.65, 'PDD': 6.28, 'JD': 8.66, 'BABA': 9.11, '0700.HK': 9.31, '3690.HK': 10.41}
	},
	'MCHI': {
		'expenses': 0.59,
		'sectors': {'Consumer Discretionary': 31.13, 'Communication Services': 21.65, 'Financials': 15.33, 'Information Technology': 5.52, 'Health Care': 5.15, 'Industrials': 4.61, 'Real Estate': 4.47, 'Consumer Staples': 3.86, 'Energy': 2.0, 'Materials': 1.85, 'Utilities': 1.81},
		'nations': {'China': 93.97, 'UK': 2.56, 'Hong Kong': 1.74, 'US': 0.48, 'Taiwan': 0.1, 'Switzerland': 0.08, 'Sweden': 0.05, 'France': 0.01},
		'holdings':{'1060.HK': 0.85, '780.HK': 0.85, 'JOBS': 1.04, 'WB': 1.11, 'SINA': 1.13, '772.HK': 1.16, 'KSFTF': 1.29, 'GSX': 1.56, 'MOMO': 1.73, 'YY': 2.1, 'TME': 2.22, 'ATHM': 2.28, 'WUBA': 2.53, 'IQ': 2.55, 'TCOM': 2.84, 'BILI': 3.74, 'VIPS': 4.32, 'TAL': 4.42, 'NTES': 4.52, 'BIDU': 5.65, 'PDD': 6.28, 'JD': 8.66, 'BABA': 9.11, '0700.HK': 9.31, '3690.HK': 10.41}
	},
	
	'FSPSX': {
		'expenses': 0.035,
		'sectors':{'Financials': 15.42, 'Health Care': 14.42, 'Industrials': 14.32, 'Consumer Staples': 11.95, 'Consumer Discretionary': 11.39, 'Information Technology': 7.81, 'Materials': 6.93, 'Communication Services': 5.31, 'Utilities': 3.97, 'Energy': 3.47, 'Real Estate': 3.11, 'Multi Sector': 1.92},
		'nations': {'Japan': 25.9, 'UK': 14.25, 'France': 10.43, 'Switzerland': 10.12, 'Germany': 8.63, 'Australia': 6.37, 'Netherlands': 4.05, 'Hong Kong': 3.28, 'Sweden': 2.82, 'Spain': 2.41, 'Denmark': 2.25, 'US': 2.13, 'Italy': 2.04, 'Singapore': 1.11, 'Finland': 1.04},
		'holdings':{'SFTBF': 0.56, 'ALIZF': 0.58, 'CBAUF': 0.58, 'KYCCF': 0.58, 'UNLVF': 0.59, 'BPAQF': 0.6, 'SNEJF': 0.64, 'DGEAF': 0.64, 'SMAWF': 0.65, 'CMXHF': 0.65, 'TTFNF': 0.71, 'BTAFF': 0.71, 'HBCYF': 0.73, 'AAIGF': 0.77, 'GLAXF': 0.8, 'SNYNF': 0.86, 'LVMHF': 0.9, 'NONOF': 0.9, 'SAPGF': 0.97, 'ASMLF': 1.08, 'AZNCF': 1.1, 'TOYOF': 1.12, 'NVSEF': 1.45, 'RHHVF': 1.89, 'NSRGF': 2.51}
	},
	'FLGR': {
		'expenses': 0.09,
		'sectors': {'Information Technology': 17.11, 'Consumer Discretionary': 15.73, 'Financials': 15.29, 'Industrials': 14.05, 'Health Care': 12.13, 'Materials': 7.78, 'Communication Services': 5.88, 'Real Estate': 5.14, 'Utilities': 3.8, 'Consumer Staples': 2.99},
		'nations': {'Germany': 98.42, 'Netherlands': 0.77, 'Spain':0.29, 'Switzerland':0.12,},
		'holdings': {'DHER.DE': 1.16, 'SYIEF': 1.18, 'MKGAF': 1.26, 'HENOF': 1.33, 'DWHHF': 1.36, 'DB': 1.46, 'FMCQF': 1.51, 'BAMXF': 1.61, 'RWNFF': 1.62, 'FSNUF': 1.67, 'ENAKF': 1.96, 'VLKPF': 2.31, 'IFNNF': 2.33, 'DDAIF': 2.56, 'DBOEF': 2.58, 'DPSTF': 2.59, 'VNNVF': 2.67, 'MURGF': 2.8, 'BFFAF': 4.23, 'ADDDF': 4.35, 'DTEGF': 4.35, 'BAYZF': 5.68, 'ALIZF': 6.43, 'SMAWF': 7.09, 'SAPGF': 10.44}
	},
	'EWG':{
		'expenses': 0.49,
		'sectors': {'Information Technology': 16., 'Consumer Discretionary': 15.55, 'Financials': 15.34, 'Industrials': 13.81, 'Health Care': 12.53, 'Materials': 7.94, 'Communication Services': 5.74, 'Real Estate': 4.86, 'Utilities': 4.28, 'Consumer Staples': 3.04},
		'nations': {'Germany':97.29, 'Netherlands':0.84, 'Spain': 0.4},
		'holdings': {'SAP.DE':12.63, 'SIE.DE': 7.59, 'ALV.DE':6.84, 'BAYN.DE': 5.39, 'DTE.DE':4.46, 'BAS.DE':4.19, 'ADS.DE':4., 'DPW.DE':3.05, 'MUV2.DE':3.01, 'DAI.DE':2.88},
	},
	
	'VGK':{
		'expenses': 0.08,
		'sectors': {'Information Technology': 7.97, 'Consumer Discretionary': 9.77, 'Financials': 15.44, 'Industrials': 14.51, 'Health Care': 15.57, 'Materials': 7.34, 'Communication Services': 4.34, 'Real Estate': 2.58, 'Utilities': 4.84, 'Consumer Staples': 12.16},
		'nations': {'UK':20.99, 'Switzerland':16.03, 'France': 14.64, 'Germany':14.52, 'Netherlands':8.19, 'Sweden':5.67, 'Spain':3.74, 'Italy':3.72, 'Denmark':3.68, 'Belgium':1.52, 'Norway':1.27, 'Ireland':.8, 'Austria': 0.49},
		'holdings': {'NESN.CH':3.44, 'ROG.CH':2.65, 'NOVN.CH':1.95, 'SAP.DE':1.84, 'AZN.GB':1.6, 'ASML.NL':1.59, 'SAN.FR':1.21, 'MC.FR':1.21, 'NOVO_B:DK':1.14, 'GSK.GB':1.06,},
	},
	
	
	'FLJP': {
		'expenses': 0.09,
		'sectors': {'Industrials': 20.61, 'Consumer Discretionary': 17.67, 'Information Technology': 12.64, 'Health Care': 11.06, 'Communication Services': 9.47, 'Financials': 8.97, 'Consumer Staples': 8.69, 'Materials': 5.49, 'Real Estate': 2.11, 'Utilities': 1.68, 'Energy': 0.6},
		'nations': {'Japan': 97.7, 'Switzerland': 0.91, 'US':0.26, 'Korea': 0.07,},
		'holdings':{'TOELF': 0.81, 'HTHIF': 0.81, 'CJPRF': 0.83, 'MZHOF': 0.86, 'NTDMF': 0.86, 'MRAAF': 0.87, 'CHGCF': 0.87, 'ALPMF': 0.89, 'FANUF': 0.93, 'HOCPF': 0.96, 'SMFNF': 1.02, 'KAOCF': 1.03, 'DKILF': 1.06, 'NTDOF': 1.18, 'RCRRF': 1.19, 'HNDAF': 1.21, 'SHECF': 1.27, 'KDDIF': 1.36, '8306.T': 1.4, 'TKPHF': 1.61, 'DSKYF': 1.62, 'SFTBF': 1.98, 'KYCCF': 2.03, 'SNEJF': 2.12, 'TOYOF': 4.21}
	},
	'EWY': {
		'expenses': 0.59,
		'sectors': {'Information Technology': 33.59, 'Communication Services': 12.15, 'Consumer Discretionary': 10.48, 'Industrials': 9.41, 'Financials': 8.89, 'Materials': 7.89, 'Health Care': 7.66, 'Consumer Staples': 6.54, 'Energy': 1.8, 'Utilities': 0.86},
		'nations': {'Korea':98.47, 'Saudi Arabia': 0.44, 'US':0.33,},
		'holdings':{'005930.KS': 21.76, '000660.KS': 6.09, '035420.KS': 4.65, '068270.KS': 3.78, '051910.KS': 2.99, '006400.KS': 2.68, '036570.KS': 2.15, '005380.KS': 1.98, '035720.KS': 1.91, '207940.KS': 1.81}
	},
	
	'FSGGX': {
		'expenses': 0.056,
		'sectors': {'Financials': 17.5, 'Consumer Discretionary': 11.77, 'Industrials': 11.17, 'Health Care': 10.38, 'Information Technology': 10.12, 'Consumer Staples': 9.83, 'Materials': 7.21, 'Communication Services': 7.12, 'Energy': 4.92, 'Multi Sector': 3.81, 'Utilities': 3.47, 'Real Estate': 2.75},
		'nations': {'Japan': 16.76, 'China': 10.39, 'UK': 9.23, 'France': 6.73, 'Canada': 6.57, 'Switzerland': 6.55, 'Germany': 5.58, 'Australia': 4.11, 'US': 3.73, 'Taiwan': 3.29, 'Korea': 3.16, 'Netherlands': 2.61, 'India': 2.13, 'Hong Kong': 2.12, 'Sweden': 1.83, 'Spain': 1.56, 'Denmark': 1.46, 'Brazil': 1.37, 'Italy': 1.32, 'South Africa': 1.02},
		'holdings':{'SHOP': 0.39, 'SNEJF': 0.41, 'DGEAF': 0.41, 'SMAWF': 0.42, 'CMXHF': 0.42, 'BTAFF': 0.46, 'TTFNF': 0.46, 'HBCYF': 0.47, 'RY': 0.47, 'AAIGF': 0.5, 'GLAXF': 0.52, 'SNYNF': 0.55, 'LVMHF': 0.58, 'NONOF': 0.58, 'SAPGF': 0.63, 'ASMLF': 0.7, 'AZNCF': 0.71, 'TOYOF': 0.72, 'NVSEF': 0.94, 'SSNLF': 0.98, 'TSM': 1.12, 'RHHVF': 1.22, '0700.HK': 1.56, 'NSRGF': 1.62, 'BABA': 1.8}
	},
	'XCEM': {
		'expenses':0.16,
		'nations': {'Taiwan': 24.39, 'Korea': 17.96, 'India': 13.73, 'Brazil': 9.9, 'Russia': 6.66, 'South Africa': 5.71, 'Thailand': 5.45, 'Malaysia': 3.26, 'Indonesia': 3.24, 'Philippines': 1.94, 'Poland': 1.52, 'Mexico': 1.37, 'Chile': 1.33, 'US': 0.99, 'UK': 0.59, 'Turkey': 0.42, 'Hong Kong': 0.36, 'France': 0.35},
		'sectors': {'Information Technology': 24.68, 'Financials': 22.53, 'Energy': 10.07, 'Materials': 9.38, 'Consumer Discretionary': 8.45, 'Communication Services': 7.08, 'Consumer Staples': 6.7, 'Industrials': 5.03, 'Utilities': 2.4, 'Health Care': 1.79, 'Real Estate': 0.55},
		'holdings':{'2330.TW': 7.29, '005930.KS': 5.94, 'HDB.BO': 3.87, 'IBN.BO': 3.1, 'INFY.BO': 3.09, 'LKOD': 2.69, 'BTS-R': 2.21, 'NPN.JO': 2.21, 'BBCA': 2.06, 'RIGD.BO': 1.94}
	},
	'EMXC': {
		'expenses': 0.25,
		'nations': {'Taiwan': 20.76, 'Korea': 19.02, 'India': 12.66, 'Brazil': 8.61, 'South Africa': 6.21, 'Russia':4.83, 'Saudi Arabia': 4.4, 'Thailand': 3.5, 'Malaysia':2.96, 'Mexico':2.47, 'Indonesia': 1.7, 'UK':1.55, 'Philippines': 1.36, 'Qatar': 1.35, 'Poland': 1.13,},
		'sectors': {'Information Technology': 23.25, 'Financials': 18.18, 'Energy': 5.95, 'Materials': 9.27, 'Consumer Discretionary': 6.53, 'Communication Services': 5.98, 'Consumer Staples': 6.14, 'Industrials': 4.03, 'Utilities': 2.11, 'Health Care': 2.72, 'Real Estate': 1.13},
		'holdings': {'INDA': 13.94, '2330.TW':8.43, '005930.KS':5.95, 'NPN.ZA':2.34, 'VALE3.BR': 1.14, '2317.TW':1.05}
	},
	
}

funds = {
	'FIPDX': {
		'expenses': 0.05,
		'regions': {'US/CA':100.},
		'nations': {'US': 100.},
		'sectors': {'Bonds': 100.},
	},
	'VGLT': {
		'expenses': 0.05,
		'regions': {'US/CA':100.},
		'nations': {'US': 100.},
		'sectors': {'Bonds': 100.},
	},
	'FUAMX': {
		'expenses': 0.03,
		'regions': {'US/CA':100.},
		'nations': {'US': 100.},
		'sectors': {'Bonds': 100.},
	},
	'SCHO': {
		'expenses': 0.05,
		'regions': {'US/CA':100.},
		'nations': {'US':100},
		'sectors': {'Bonds': 100.},
	},
	'MINT': {
		'expenses': 0.36,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	'IGOV': {
		'expenses': 0.35,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	
	'VCLT': {
		'expenses': 0.05,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	'VCSH': {
		'expenses': 0.05,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	'LQD': {
		'expenses': 0.14,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	'AGG': {
		'expenses': 0.04,
		'regions': {'US/CA':100.},
		'nations': {'US':100.},
		'sectors': {'Bonds': 100.},
	},
	'IAGG': {
		'expenses': 0.09,
		'nations': {'Japan':11.68, 'France': 6.66, 'Italy': 6.23, 'UK': 6.17, 'China': 7.89, 'Germany': 4.83, 'Spain': 4.21, 'Korea':2.35, 'Belgium': 1.74},
		'regions': {'US/CA':8.95, 'Latin America': 1.04, 'Asia': 22.51, 'Europe':60.15},
		'sectors': {'Bonds': 100.},
	},
	
	'IAU': {
		'expenses': 0.25,
		'commodities': {'gold': 100.},
		'sectors': {'Commodities': 100.},
	},
}

regions = {
	'North America': ['US', 'Canada'],
	'Latin America': ['Mexico', 'Brazil', 'Ecuador', 'Puerto Rico', 'Peru', 'Argentina', 'Columbia', 'Venezuela', 'Chile',],
	'West Europe': ['Germany', 'UK', 'Ireland', 'France', 'Switzerland', 'Luxembourg', 'Spain', 'Italy', 'Austria', 'Belgium', 'Netherlands',],
	'North Europe': ['Denmark', 'Sweden', 'Norway', 'Finland'],
	'East Europe': ['Russia', 'Poland', 'Serbia'],
	'East Asia': ['China', 'Taiwan', 'Hong Kong', 'Japan', 'Korea', 'Malaysia', 'Vietnam', 'Thailand', 'Singapore'],
	'South Asia': ['India', 'Pakistan', 'Bangladesh'],
	'Middle East': ['Turkey', 'Egypt', 'Iran', 'Saudi Arabia', 'Israel'],
	'Africa': ['Ethiopia', 'Congo', 'DRC', 'South Africa', 'Nigeria'],
	'Oceania': ['Australia', 'New Zealand', 'Indonesia', 'Philippines'],
}
