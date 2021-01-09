
import sys, os
from pathlib import Path
from bs4 import BeautifulSoup

from yahooquery import Ticker
import yfinance as yf

URLS = {
    'EQUITY': {
        'full': 'https://snapshot.fidelity.com/fidresearch/snapshot/landing.html#/research?symbol={ticker}&appCode=',
        'snapshot': 'https://eresearch.fidelity.com/eresearch/evaluate/snapshot.jhtml?symbols={ticker}',
        'quote': 'https://eresearch.fidelity.com/eresearch/evaluate/quote.jhtml?symbols={ticker}',
        'news': 'https://eresearch.fidelity.com/eresearch/evaluate/news/basicNews.jhtml?symbols={ticker}',
        'analyst': 'https://eresearch.fidelity.com/eresearch/evaluate/analystsOpinions.jhtml?symbols={ticker}',
        'stats': 'https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/keyStatistics.jhtml?stockspage=keyStatistics&symbols={ticker}',
        'earnings': 'https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/earnings.jhtml?symbols={ticker}',
        'dividends': 'https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/dividends.jhtml?symbols={ticker}',
        'financials': 'https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/financials.jhtml?stockspage=financials&symbols={ticker}',
        'history': 'https://eresearch.fidelity.com/eresearch/evaluate/analystsOpinionsDetails.jhtml?symbols={ticker}&firmId=99999&firm=Equity%20Summary%20Score',
        'basket': 'https://research2.fidelity.com/fidelity/screeners/etf/etfholdings.asp?symbol={ticker}&view=Exposure',
        
    },
    
    'ETF': {
        'snapshot': 'https://screener.fidelity.com/ftgw/etf/snapshot/snapshot.jhtml?symbols={ticker}',
        'quote': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/quote.jhtml?symbols={ticker}',
        'composition': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/portfolioComposition.jhtml?symbols={ticker}',
        'news': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/newsEvents.jhtml?symbols={ticker}',
        'analyst': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/analystOpinions.jhtml?symbols={ticker}',
        'stats': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/keyStatistics.jhtml?symbols={ticker}',
        'expenses': 'https://screener.fidelity.com/ftgw/etf/goto/snapshot/distributions.jhtml?symbols={ticker}',
        'holdings': 'https://research2.fidelity.com/fidelity/screeners/etf/etfholdings.asp?symbol={ticker}&view=Region',

    },
    
}

TYPES = {
    'EQUITY': ['TSLA', 'AMD', 'NVDA', 'BABA', 'TCEHY', 'AMZN', 'MSFT', 'COST', 'NTDOY', 'DIS', 'SHOP',
               'PDD', 'GOOGL', 'AAPL', 'BIDU', 'SNE', 'FB', 'PYPL', 'NFLX', 'NIO', 'WDC'],
    'ETF': ['SPY', 'VXF', 'VTI', 'IWV', 'VONG', 'XITK', 'KOMP', 'SOCL', 'ESPO', 'CIBR', 'SKYY', 'LIT', 'IBB',
            'FHLC', 'FIDU', 'FNCL', 'FMAT', 'PHO', 'ACES', 'ICLN', 'PBW', 'ASHR', 'CNYA', 'KWEB', 'MCHI', 'SPDW',
            'VGK', 'EWG', 'FLJP', 'EWY', 'EWC', 'IXUS', 'EMXC', 'ICVT', 'CWB', 'SCHP', 'IGOV', 'GOVT', 'LQD', 'AGG',
            'IAGG', 'IAU', 'DBC'],
}

STRATEGY = {
    'companies': {
        'TSLA': 2.5,
        'AMD': 2,
        'NVDA': 2,
        'BABA': 2,
        'TCEHY': 1.5,
        'AMZN': 1,
        'MSFT': 1,
        'COST': 1,
        'NTDOY': 1,
        'DIS': 1,
        'SHOP': 0.5,
        'PDD': 0.5,
        'GOOGL': 0.5,
        'AAPL': 0.5,
        'BIDU': 0.5,
        'SNE': 0.5,
        'FB': 0.5,
        'PYPL': 0.5,
        'NFLX': 0.5,
        'NIO': 0.5,
        # 'LI': 0.5,
        # 'XPEV': 0.5,
        'WDC': 0,
    },
    
    'markets/sectors': {
        # general
        'SPY': 6,
        'VXF': 4,
        'VTI': 4,
        'IWV': 1,
        
        # tech
        'VONG': 3,
        'XITK': 2,
        'KOMP': 1,
        'SOCL': 1,
        'ESPO': 1,
        'CIBR': 1,
        'SKYY': 1,
        'LIT': 1,
        'IBB': 1,
        
        # sectors
        'FHLC': 2,
        'FIDU': 1,
        'FNCL': 1,
        'FMAT': 1,
        
        # energy
        'PHO': 1,
        'ACES': 3,
        'ICLN': 3,
        'PBW': 1,
    },
    
    'international': {
        # China
        'ASHR': 6,
        'CNYA': 4,
        'KWEB': 3,
        'MCHI': 2,
        
        # EU/J
        'SPDW': 3,
        'VGK': 1.5,
        'EWG': 0.5,
        'FLJP': 2,
        'EWY': 0.5,
        'EWC': 0.5,
        
        # ex-US
        'IXUS': 3,
        'EMXC': 4,
    },
    
    'diverse': {
        # convertible bonds
        'ICVT': 5,
        'CWB': 0,
        
        # bonds - treasury
        'SCHP': 1,
        'IGOV': 1,
        'GOVT': 0,
        
        # bonds - corporate
        'LQD': 1,
        'AGG': 0.5,
        'IAGG': 0.5,
        
        # commodity
        'IAU': 1,
        'DBC': 0,
    }
}

FUNDS = {
    'FZROX',
    'FSMAX',
    'FZIPX',
    
    'FSPTX',
    
    'FHKCX',
    'FSPSX',
    'FSGGX',
    
    'FUAMX',
}

REGIONS = {
    'United States': 'North America', 'China':'Asia', 'Japan': 'Asia',
                'Canada': 'North America', 'United Kingdom': 'Europe',
    'Switzerland': 'Europe', 'Singapore': 'Asia', 'Russia':'Europe',
                'India':'Asia', 'Sweden':'Europe', 'Puerto Rico': 'Latin America', 'Taiwan': 'Asia',
            'Netherlands': 'Europe', 'Germany': 'Europe', 'Hong Kong': 'Asia', 'Brazil': 'Latin America',
            'Israel': 'Middle East', 'South Korea': 'Asia', 'Spain': 'Europe', 'Belgium': 'Europe',
            'Chile': 'Latin America', 'Argentina': 'Latin America', 'Turkey': 'Middle East', 'France': 'Europe',
            'British Virgin Islands': 'Asia', 'Poland': 'Europe', 'Australia': 'Asia',
            'Ireland': 'Europe', 'Denmark': 'Europe', 'Kazakhstan': 'Asia', 'New Zealand': 'Asia',
            'Austria': 'Europe', 'Norway': 'Europe', 'Italy': 'Europe', 'Finland': 'Europe', 'Portugal': 'Europe',
            'Macao': 'Asia', 'Egypt': 'Middle East', 'Papua New Guinea': 'Asia', 'Vietnam': 'Asia',
            'Burkina Faso': 'Africa', 'Mexico': 'Latin America', 'Malta': 'Europe', 'Indonesia': 'Asia',
            'Luxembourg': 'Europe', 'United Arab Emirates': 'Middle East', 'Ukraine': 'Europe',
            'Liechtenstein': 'Europe', 'Guernsey': 'Africa', 'South Africa': 'Africa', 'Saudi Arabia': 'Middle East',
            'Qatar': 'Middle East', 'Kuwait': 'Middle East', 'Thailand': 'Asia', 'Malaysia': 'Asia', 'Peru': 'Latin America',
            'Hungary': 'Europe', 'Philippines': 'Asia', 'Colombia': 'Latin America', 'Czech Republic':'Europe',
            'Greece':'Europe', 'Pakistan':'Asia', 'Romania':'Europe', 'Panama':'Latin America',
            'Uruguay':'Latin America', 'Slovakia':'Europe',
            'Slovenia': 'Europe', 'Bulgaria': 'Europe', 'Cyprus': 'Europe', 'Lithuania': 'Europe',
            'Croatia': 'Europe', 'Iceland': 'Europe', 'Latvia': 'Europe',
}


_yf_tickers = {}
def get_yf(ticker):
    if ticker not in _yf_tickers:
        _yf_tickers[ticker] = yf.Ticker(ticker)
    return _yf_tickers[ticker]

_yq_tickers = {}
def get_yq(ticker):
    if ticker not in _yq_tickers:
        _yq_tickers[ticker] = Ticker(ticker)
    return _yq_tickers[ticker]

def purge_tickers():
    _yq_tickers.clear()
    _yf_tickers.clear()

def get_ticker(ticker):
    if isinstance(ticker, str):
        return get_yq(ticker)
    return ticker

def get_type(ticker):
    ticker = get_ticker(ticker)
    return next(iter(ticker.quotes.values()))['quoteType']

def get_recommendations(ticker):
    ticker = get_ticker(ticker)
    return [row['symbol'] for row in next(iter(ticker.recommendations.values()))['recommendedSymbols']]
    
def get_fund_holdings(ticker):
    ticker = get_ticker(ticker)
    if get_type(ticker) != 'ETF':
        return
    x = ticker.fund_top_holdings
    return dict(zip(x['symbol'].to_list(), x['holdingPercent'].to_list()))

def get_fund_categories(ticker):
    ticker = get_ticker(ticker)
    if get_type(ticker) != 'ETF':
        return
    info = ticker.fund_category_holdings
    return {'stocks':info['stockPosition'][0], 'bonds':info['bondPosition'][0]}

def get_fund_sectors(ticker):
    ticker = get_ticker(ticker)
    if get_type(ticker) != 'ETF':
        return
    return dict(zip(ticker.fund_sector_weightings.index.to_list(),
                    ticker.fund_sector_weightings.to_numpy().reshape(-1).tolist()))

_nans = {'--', 'N/A', 'Not Available', None}

def _fmt_human(s):
    scales = {'K':1e3, 'M':1e6, 'B':1e9, 'G':1e9, 'T':1e12}
    factor = 1.
    if s in _nans:
        return None
    s = s.replace(',', '')
    if s[-1] in scales:
        factor *= scales[s[-1]]
        s = s[:-1]
    try:
        if s[0] not in '.0123456789':
            s = s[1:]
        s = float(s)*factor
    except:
        # print(s)
        raise
    
    return s

def _fmt_percent(s):
    try:
        if s in _nans:
            return None
        s = s.replace(',', '')
        if s[-1] in '%':
            s = s[:-1]
        return float(s)
    except:
        # print(s)
        raise

def _fmt_online(s):
    s = s.replace('&amp;', '&')
    return s

def extract_table(table, split_dates='AS OF', row_type='tr', col_types=['th', 'td']):
    data = []
    rows = table.find_all(row_type)
    if not isinstance(col_types, (list,tuple)):
        col_types = col_types,
    for row in rows:
        cols = []
        for ct in col_types:
            cols.extend(ele.text.strip() for ele in row.find_all(ct))
        cols = [_fmt_online(c) for c in cols if len(c)]
        data.append(cols)
        
    if split_dates is not None:
        dates = []
        for row in data:
            if len(row) and split_dates in row[0]:
                key, date = row[0].split(split_dates)
                row[0] = key
                dates.append([f'{key.strip()} date'] + [None]*(len(row)-2) + [date.strip()])
        data.extend(dates)
    
    # format numbers
    # for r, row in enumerate(data):
    #     for c, raw in enumerate(row):
    #         try:
    #             data[r][c]
    
    return data

def extract_html(path):
    try:
        path = Path(path)
    
        rawhtml = path.open('rb').read()#.decode()
        bs = BeautifulSoup(rawhtml,features="lxml")
        return bs
    except:
        print(path)
        raise
    
def _pie_fmt(table):
    for row in table:
        if len(row) == 3:
            del row[1]
        assert len(row) == 2, str(row)
        if len(row[1]):
    
            if row[1] not in _nans:
                row[1] = None
            else:
                row[1] = float(row[1][:-1])/100
        
    return dict(table)

def _extract_analyst(table):
    rows = table.findAll('tr')[2:]
    
    def _fmt_factset(row):
        els = row.findAll('td')
        grade = {'F': 1, 'D': 2, 'C': 3, 'B': 4, 'A': 5, '': None}
        g = els[3].text.strip().split('\n')[0]
        raw = g
        if len(g) > 1:
            g = g[0]
        if g not in grade:
            return raw
        return grade[g]
    
    def _fmt_morning(row):
        els = row.findAll('td')
        return int(list(els[3].children)[0].attrs['alt'][0])
    
    analysts = {'FactSet': _fmt_factset, 'Morningstar, Inc.': _fmt_morning}
    
    results = {}
    for row in rows:
        els = row.findAll('td')
        title = els[0].text.replace('*', '')
        assert title in analysts, f'unknown analyst: {title}'
        
        results[title] = analysts[title](row)
        
    return results

def _extract_info(table):
    keys = [t.text for t in table.find_all('h4')][:9]
    # print(keys)
    dt = keys[2].split(' ')[-1]
    keys[2] = 'Net Assets'
    
    vals = [t.text for t in table.find_all('p')[4:13]]
    vals[2] = _fmt_human(vals[2])
    vals[3] = _fmt_percent(vals[3])
    info = dict(zip(keys,vals))
    info['Net Assets date'] = dt
    return info
    
def _extract_factset(table):
    names = [t.text for t in table.find_all('h4')][-3:]
    nums = []
    for t in table.find_all('span', {'class': 'etfcom-ratingtext'}):
        txt = t.text
        try:
            nums.append(int(txt))
        except ValueError:
            nums.append(txt)
    assert len(names) == len(nums), f'{names} vs {nums}'
    # print(names, nums)
    return dict(zip(names, nums))
    
def _extract_stats(table):
    
    stats = extract_table(table)
    
    # key1, dt1 = stats[-2][0].split('AS OF ')
    # stats[-2][0] = key1
    # key2, dt2 = stats[-1][0].split('AS OF ')
    # stats[-1][0] = key2
    #
    # stats = dict(stats)
    # stats[f'{key1} date'] = dt1
    # stats[f'{key2} date'] = dt2
    
    stats = dict(stats)
    
    for k, v in stats.items():
        try:
            if v in _nans:
                stats[k] = None
            else:
                stats[k] = float(v[:-1] if '%' in v else v)
        except:
            stats[k] = v
    
    return stats
    
def _extract_compare(table):
    
    info = extract_table(table)
    
    info[0].insert(0, None)
    
    info[1][-1] = _fmt_human(info[1][-1])
    info[1][-2] = _fmt_human(info[1][-2])
    
    for row in info[2:]:
        if ' date' not in row[0]:
            row[-2] = _fmt_percent(row[-2])
            row[-1] = _fmt_percent(row[-1])
    
    return info


def load_etf_pie(path):
    bs = extract_html(path)
    tbs = bs.findAll("table")
    
    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0]
    
    info = dict(extract_table(tbs[1]))
    
    inds = {
        'Equity': [None, None, None, 'Holdings', 'Sector Exposure', 'Industry Exposure', 'Regional Exposure',
                   'Country Exposure', 'Market Capitalization'],
        'Fixed Income': [None, None, None, 'Holdings', 'Debt Type', 'Regional Exposure',
                         'Country Exposure', 'Credit Grade', 'Maturity'],
        'Multi-Asset': [None, None, None, 'Holdings', 'Regional Exposure', 'Country Exposure'],
        'Commodity': [None, None, None, 'Holdings', 'Regional Exposure', 'Country Exposure'],
    }
    try:
        inds = inds[info['Asset Classification']]
    except:
    
        print(f'{ticker} {len(tbs)}, {path}')
        raise

    missing = [x.text.strip().replace('Sorry : ', '').replace(' is not available for this symbol.', '')
               for x in bs.find_all('div', {'class': "error-message"})]
    
    for m in missing:
        m = m.lower()
        try:
            idx = [i for i, x in enumerate(inds) if x is not None and m.startswith(x.lower())][0]
            # inds.remove(m)
            del inds[idx]
        except:
            print(f'{m} {ticker} {path} {len(tbs)} {missing} {info}')
            raise
    
    tables = {}
    for i, key in enumerate(inds):
        if key is not None:
            try:
                tables[key] = extract_table(tbs[i])
            except:
                print(f'{ticker} {key} {i} {len(tbs)}, {path}')
                raise
    
    tables['Holdings'] = tables['Holdings'][1:]
    
    for key, tb in tables.items():
        for row in tb:
            if len(row) == 3:
                del row[1]
            row[-1] = _fmt_percent(row[-1])

        info[key] = dict(tb)
        # try:
        #     tables[key] = dict(tb)
        # except:
        #     tables[key] = tb
        
    return ticker, info

def load_etf_holdings(path):
    bs = extract_html(path)
    
    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0]
    table = bs.findAll("table", {"class": "results-table sortable"})[0]
    
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values
    
    data = data[1:]
    for i, row in enumerate(data):
        if len(row) == 2:
            row.insert(0, '-CASH-')
            row.insert(2, None)
        elif len(row) == 3:
            row.insert(0, None)
        if len(row) != 4:
            print(row)
        if row[-1] in _nans:
            row[-1] = None
        else:
            row[-1] = float(row[-1]) / 100
    return ticker, data

def load_etf_snapshot(path):
    bs = extract_html(path)

    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0]
    tbs = bs.find_all('table')
    
    inds = {
        'analyst': 15,
        'info': 1,
        'ratings': 1,
        'stats': 17,
        'compare': 18,
    }
    extraction = {
        'analyst': _extract_analyst,
        'info': _extract_info,
        'ratings': _extract_factset,
        'stats': _extract_stats,
        'compare': _extract_compare,
    }
    
    out = {}
    for n, i in inds.items():
        try:
            out[n] = extraction[n](tbs[i])
        except:
            print(ticker, n)
            raise
    return ticker, out
    
def load_etf_analyst(path):
    
    bs = extract_html(path)

    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0]
    try:
        results = _extract_analyst(bs.findAll("table")[1])
        return ticker, results
    except:
        print(f'failed: {ticker}')
        raise

    
def _stock_analysts(table):
    grades = extract_table(table.find_all('div', {'class': "census-table"})[0].find_all('table')[0])[0]
    grades = dict(x[:-1].split('(') for x in grades)
    grades = {k: int(v) for k, v in grades.items()}

    options = []
    ratings = table.find_all('tbody')
    for rate in ratings:
        options += extract_table(rate)[1:]
    for row in options:
        try:
            if not len(row[1]):
                row[1] = None
            if row[1][-1] == '%':
                row[1] = row[1][:-1]
            row[1] = float(row[1])  # /100
        except:
            print(row)
            raise

    verdict = table.find_all('div', {'class': "bullish"})[0].text
    
    try:
        if len(verdict):
            terms = verdict.split(' ')
            verdict, score = ' '.join(terms[:-1]), terms[-1]
            score = float(score[1:-1])
        else:
            score, verdict = None, None
    except ValueError:
        print(verdict)
        raise
    
    return {'score':score, 'verdict':verdict, 'grades':grades, 'analysts':options}
    
def _stock_company(table):
    sector, industry = [x.text.strip() for x in table.find_all('span', {'class': 'right'})[:2]]

    elms = table.find_all('p')
    info = [el.text for el in elms]
    start_idx = [i for i, x in enumerate(info) if 'Executives' in x][0] + 1
    end_idx = [i for i, x in enumerate(info) if x.startswith('Environmental, Social, and')][0]
    *base_people, addr, phone = elms[start_idx:end_idx]

    execs = None
    els = table.find('div', {'id': "executives"})
    if els is not None:
        people = [el.text.strip() for el in els.find_all('li')]
    else:
        people = base_people
    if len(people):
        execs = {}
        try:
            for name, job in [person.split(',\xa0') for person in people]:
                if name not in execs:
                    execs[name] = []
                execs[name].append(job)
        except TypeError:
            print(people)
            raise

    addr = addr.text.replace('\r', ', ').replace('\n', '').replace('\t', '').replace('\xa0', ' ').replace(
        ' of America', '')
    country = addr.split(', ')[-1]
    phone = phone.text
    
    data = {'sector':sector, 'industry':industry, 'address': addr, 'country': country, 'phone': phone,
            'description': table.find_all('div', {'class': "hidden", "id": "busDesc-more"})[0].find_all('p')[0].text}
    if execs is not None:
        data['execs'] = execs
    
    idx = [i for i, el in enumerate(elms) if 'Employees:' in  str(el)][0]
    try:
        data['employees'] = int(elms[idx].text.split('\xa0')[-1].replace(',', ''))
    except:
        pass
    
    return data

def _stock_news(table):
    link_root = 'https://eresearch.fidelity.com'

    raw = table.find_all('li', {'class': 'news-item'})
    
    stories = []
    for row in raw:
        story = {
            'title': row.find('h3').text.strip(),
        }
        
        story['source'], story['date'] = [x.strip() for x in
                                          row.find('div', {'class': 'source'}).text.strip().split(' – ')]
        desc = row.find('p')
        if desc is not None:
            story['description'] = desc.text.strip()
        
        links = row.find_all('a')
        if len(links) > 1:
            story['link'] = link_root + links[1]['href']
        
        stories.append(story)
        
    return stories
    
def _stock_event(table):
    cal = table.find('div', {'class': 'calander'})
    if cal is not None:
        month = cal.find('div', {'class': 'month'}).text.strip()
        day = cal.find('div', {'class': 'date'}).text.strip()
        event = table.find('div', {'class': 'right-content'}).find('p').text.strip()
        return {'name':event, 'month':month, 'day':day}
    
def _stock_compare(table):
    tb = extract_table(table)

    row_fmts = {1: _fmt_human, 2: _fmt_percent, 3: float, 4: _fmt_human, 5: _fmt_human, 6: _fmt_percent, 7: float,
                8: _fmt_human,
                9: _fmt_human, 10: _fmt_percent, 11: _fmt_human, 12: _fmt_percent}

    for r, fn in row_fmts.items():
        for c, raw in enumerate(tb[r]):
            try:
                tb[r][c] = fn(raw)
            except ValueError:
                pass

    for row in tb:
        if row[-1] is not None and len(row[-1]) > 2 and row[-1][-2:] in {'st', 'nd', 'rd', 'th'}:
            row[-1] = int(row[-1][:-2])
            
    return tb
    
def _stock_basics(table):
    tb = extract_table(table)
    
    tb[0][-1] = float(tb[0][-1])
    tb[1][-1] = int(tb[1][-1])
    tb[2][-1] = float(tb[2][-1])
    tb[3][-1] = int(tb[3][-1])

    tb[4][-1] = float(tb[4][-1])
    tb[5][-1] = float(tb[5][-1])
    tb[6][-1] = float(tb[6][-1])

    try:
        val, date = tb[8][-1][:-10], tb[8][-1][-10:]
        tb[8][-1] = float(val)
    except:
        print(tb[8], val)
        raise
    tb.append(['52-Week High Date', date])

    try:
        val, date = tb[9][-1][:-10], tb[9][-1][-10:]
        tb[9][-1] = float(val)
    except:
        print(tb[9], val)
        raise
    tb.append(['52-Week Low Date', date])
    
    tb[10][-1] = _fmt_percent(tb[10][-1])

    tb[12][-1] = _fmt_human(tb[12][-1])
    tb[13][-1] = _fmt_human(tb[13][-1])

    bad = []
    for i, row in enumerate(tb):
        if row[0].startswith('Index'):
            bad.append(i)
    for i in bad:
        del tb[i]
    
    return dict(tb)

def load_stock_snapshot(path):
    
    bs = extract_html(path)

    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0].strip()

    current = None

    tbs = bs.find_all('table')

    inds = {
        'basics': 2,
        'analyst': 13,
        'company': 13,
        'news': 13,
        'event': 13,
        'compare': -2,
    }
    extraction = {
        'basics': _stock_basics,
        'analyst': _stock_analysts,
        'company': _stock_company,
        'news': _stock_news,
        'event': _stock_event,
        'compare': _stock_compare,
    }

    out = {}
    for n, i in inds.items():
        try:
            out[n] = extraction[n](tbs[i])
        except:
            print(ticker, n, path)
            raise
        
    if 'company' in out:
        base = out['company']
        base['ticker'] = ticker
        base['name'] = bs.find('h2', {'id':'companyName'}).text.strip()
        base['name'] = ' '.join(n.capitalize() for n in base['name'].split(' '))
        
    if 'basics' in out:
        base = out['basics']
        base['last'] = bs.find('span', {'class':"symbol-value-sub", 'id':"lastPrice"}).text.strip()
        base['change'] = bs.find('span', {'id':"netChgToday"}).text.strip()
        base['percent_change'] = float(bs.find('span', {'id':"pctChgToday"}).text.strip()[1:-3])
        
    return ticker, out
    
def load_stock_history(path):

    bs = extract_html(path)

    ticker = bs.findAll('title')[0].contents[0].split(' | ')[0].strip()

    tb = bs.find_all('table')[15]

    rows = tb.find_all('tr')
    info = [[el.text.strip() for el in row.find_all('span')] for row in rows]
    for row in info[1:]:
        del row[1]
        row[2:] = [float(n) for n in row[2:]]
    
    return ticker, {'headers':info[0], 'data':info[1:]}
    
def load_stock_contained(path):
    
    bs = extract_html(path)
    
    ticker = bs.find('h1').text.replace('ETPs Holding ', '').replace(' in Basket', '')

    data = extract_table(bs.find("table"))
    for row in data[1:]:
        row[3] = _fmt_percent(row[3])
        row[4] = _fmt_human(row[4])
        row[5] = _fmt_percent(row[5])
        row[6] = _fmt_human(row[6])
        row[7] = float(row[7])
    
    return ticker, data
    






























