from datetime import datetime
import time
import yfinance as yf
import requests

tickers = ["TSLA","AAPL","MSFT","AMZN","GOOGL","RELIANCE.NS","TCS.NS","HSBA.L","0700.HK"]

def try_yf_download(ticker):
    print('\n--- yf.download', ticker)
    try:
        df = yf.download(ticker, start=datetime(2016,1,1), end=datetime.now(), progress=False)
        print('yf.download empty:', df.empty)
        return not df.empty
    except Exception as e:
        print('yf.download error:', type(e), e)
        return False

def try_ticker_history(ticker):
    print('\n--- Ticker.history', ticker)
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period='1mo')
        print('Ticker.history rows:', len(df))
        return not df.empty
    except Exception as e:
        print('Ticker.history error:', type(e), e)
        return False

def try_yahoo_csv(ticker):
    print('\n--- direct Yahoo CSV', ticker)
    period1 = int(time.mktime(datetime(2016,1,1).timetuple()))
    period2 = int(time.time())
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1d&events=history'
    try:
        r = requests.get(url, timeout=15)
        print('status:', r.status_code, 'len:', len(r.content))
        if r.status_code == 200 and len(r.content) > 50:
            print(r.text.splitlines()[:5])
            return True
        return False
    except Exception as e:
        print('requests error:', type(e), e)
        return False

for t in tickers:
    print('\n===', t)
    ok1 = try_yf_download(t)
    ok2 = try_ticker_history(t)
    ok3 = try_yahoo_csv(t)
    print('RESULTS:', t, {'yf_download': ok1, 'ticker_history': ok2, 'yahoo_csv': ok3})
