

nations = {
	'Canada': 'EWC',
	'US': 'SPY',
	'Mexico': 'EWW',
	'Peru': 'EPU',
	'Brazil': 'EWZ',
	'Argentina': 'ARGT',
	'UK': 'EWU',
	'Spain': 'EWP',
	'Germany': 'EWG',
	'Italy': 'EWI',
	'Russia': 'ERUS',
	'Egypt': 'EGPT',
	'Africa': 'AFK',
	'S. Africa': 'EZA',
	'India': 'INDA',
	'Korea': 'EWY',
	'China': 'MCHI',
	'Singapore': 'EWS',
	'Australia': 'EWA',
	'Japan': 'EWJ',
}

sectors_full = {
	'basic_materials': ['XLB', 'XME'],
	'cons-cyc': ['XLY', 'XHB', 'PBS', 'XRT', 'PEJ'],
	'cons-ncyc': ['XLP', 'PBJ'],
	'energy': ['XLE', 'IEZ', 'XOP'],
	'financial': ['XLF', 'KBWB', 'IAI', 'KBWI', 'IYG'],
	'healthcare': ['XLV', 'IBB', 'IHI', 'IHE', 'XHE', 'IHF'],
	'industrial': ['XLI', 'PPA', 'IYT', 'PKB'],
	'real estate': ['IYR', 'VNQ'],
	'tech': ['XLK', 'FDN', 'XSD', 'IGV'],
	'telecom': ['IYZ', 'VOX'],
	'utilities': ['XLU', 'VPU']
}

sectors = {
	'basic_materials': 'XLB',
	'cons-cyc': 'XLY',
	'cons-ncyc': 'XLP',
	'energy': 'XLE',
	'financial': 'XLF',
	'health care': 'XLV',
	'industrial': 'XLI',
	'real estate': 'IYR',
	'tech': 'XLK',
	'telecom': 'IYZ',
	'utilities': 'XLU',
}

bonds = {
	'LQD': 'Corporate',
	'SPSB': 'Short Corporate',
	'SHY': 'Treasury',
	'JNK': 'High Yield',
	'AGG': 'Aggregate',
	'MINT': 'Ultrashort',
	'VTIP': 'Inflation Protected',
	'IGLB': 'Long Term Corporate',
	'VCLT': 'Long Term Corporate',
	'TLT': 'Long Treasury',
}


commodities = {
	'GLD': 'Gold',
	'SLV': 'Silver',
	'USO': 'Oil',
	'DBC': 'Various',
	'UNG': 'Natural Gas',
	'DBA': 'Agriculture',
}

forex = {
	'UUP': 'US Dollar',
	'FXY': 'Yen',
	'FXE': 'Euro',
	'FXF': 'Swiss Franc',
	'FXB': 'British Pounds',
	'FXC': 'Can Dollar',
	'FXA': 'Aus Dollar',
	'CYB': 'Yuan',
}

canada = {
	'CDZ': 'Canada',
	'VI': 'ex-NA',
	'XRE': 'Canadian Real Estate',
	'VFV': 'Canada SnP',
	'SPY': 'SnP',
	'VOO': 'SnP',
	'QQQ': 'NasDaq',
	
	'IXJ': 'Healthcare',
	
	'XFN': 'Banks',
	'XUT': 'Utilities',
	
}

rec = {
	'VTF': 'Tech',
	'XLV': 'Healthcare',
	'QQQ': 'NasDaq',
	'IWF': 'mid',
	
	'ARKK': 'innovative',
	
	'AIQ': 'Robotics', # mostly US (amazon, nvidia, netflix, tencent, alibaba...)
	'ROBO': 'Robotics', # US + Japan (nvidia, ? ...)
	'BOTZ': 'Robotics', # mostly Japan (nvidia, ? ...)
	
	'SOCL': 'Social Media',
	'HACK': 'Cybersecurity',
	'SKYY': 'Cloud Storage',
	
	'LIT': 'Lithium Batteries',
	'ICLN': 'Clean Energy',
	'IBB': 'Bio Tech',
	'ITA': 'National Defense',
	
	'GMF': 'Emerging',
	'PHO': 'Water',
}

china = { # index: CSE 300
	'ASHR': 'Consumer Focused',
	'PGJ': 'Other',
	'CNYA': 'China A',
	
}

stox = {
	
	'UPWK': 'Upwork', # Freelance work
	'CIT': 'Bank',
	'SHOP': 'Shopify', # online shopping
	'EA': 'Gaming',
	'CSCO': 'Cisco', # competitor to huawei
	'NFLX': 'Netflix',
	'MSFT': 'Microsoft',
	
}

markets = {
	'BABA': 'Alibaba',
	'AMZN': 'Amazon',
	'AAPL': 'Apple',
	'GOOG': 'Google',
	'NFLX': 'Netflix',
	'FB': 'Facebook',
	'TSLA': 'Tesla',
	'AMD': 'AMD',
	'BIDU': 'Baidu',
	'IBM': 'IBM',
	'INFY': 'Infosys',
	'DTE.DE': 'Telekom',
	'NVDA': 'nVidia',
	'INTC': 'Intel',
	'MSFT': 'Microsoft',
	'NOK': 'Nokia',
	'SAP.DE': 'SAP',
	'PYPL': 'Paypal',
	'ZM': 'Zoom',
	'TWTR': 'Twitter',
	'0700.HK': 'Tencent',
	'COST': 'Costco',
	'KHC': 'Kraft',
	'MCD': 'McDonalds',
	'KO': 'Coca-Cola',
	'SAOC': 'Saudi Oil',
	
	'GLD': 'Gold',
	'DBC': 'Commodities',
	
	'SPY': 'S&P',
	'QQQ': 'Nasdaq',
	
	'ASHR': 'China',
	'INDA': 'India',
	'RSX': 'Russia',
	'EWG': 'Germany',
	'EEM': 'Emerging Markets',
	
	'TLT': 'Long Treasury Bonds',
	'SHY': 'Short Treasury Bonds',
	'VCLT': 'Long Corporate Bonds',
	'LQD': 'Corporate Bonds',
	'SPSB': 'Short Corporate Bonds',
	'JNK': 'High Yield Bonds',
	'MINT': 'Ultrashort Bonds',
	
	'AARK': 'Innovative',
	
	'UPWK': 'Upwork',  # Freelance work
	'CIT': 'Bank',
	'SHOP': 'Shopify',  # online shopping
	'EA': 'Gaming',
	'CSCO': 'Cisco',  # competitor to huawei
}



