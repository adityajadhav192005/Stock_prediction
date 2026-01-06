import requests, time
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

tickers = ["TSLA","AAPL","MSFT","AMZN","GOOGL","RELIANCE.NS","TCS.NS","HSBA.L","0700.HK"]
period1 = int(time.mktime(datetime(2016,1,1).timetuple()))
period2 = int(time.time())

for t in tickers:
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{t}?period1={period1}&period2={period2}&interval=1d&events=history'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(t, 'status', r.status_code, 'len', len(r.content))
        if r.status_code == 200 and len(r.content) > 50:
            print(r.text.splitlines()[:3])
    except Exception as e:
        print('error', t, e)
