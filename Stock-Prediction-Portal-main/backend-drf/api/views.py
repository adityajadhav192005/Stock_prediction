from rest_framework.views import APIView
from .serializers import StockPredictionSerializer
from rest_framework.response import Response
from rest_framework import status
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from .utils import save_plot
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests
import time
from io import StringIO
import traceback
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache


# Create your views here.

class StockPredictionAPIView(APIView):
    def post(self, request):
        serializer = StockPredictionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticker = serializer.validated_data['ticker']
            mode = serializer.validated_data.get('mode', 'live')

            # Prepare cache directory (file-based cache backend) for fetched data
            cache_location = settings.CACHES.get("default", {}).get("LOCATION")
            if cache_location:
                os.makedirs(str(cache_location), exist_ok=True)

            def _cache_key(symbol, start_dt, end_dt):
                return f"stock-data:{symbol}:{start_dt.date()}:{end_dt.date()}"

            def _load_cache(cache_key):
                cached = cache.get(cache_key)
                if not cached:
                    return None
                try:
                    df_cached = pd.read_json(StringIO(cached), orient="split")
                    if "Date" in df_cached.columns:
                        df_cached["Date"] = pd.to_datetime(df_cached["Date"])
                        df_cached = df_cached.set_index("Date")
                    if not df_cached.empty:
                        return df_cached
                except Exception:
                    return None
                return None

            def _save_cache(cache_key, df):
                try:
                    df_reset = df.reset_index()
                    cache.set(cache_key, df_reset.to_json(orient="split"), timeout=settings.LIVE_DATA_CACHE_TTL)
                except Exception:
                    pass

            def fetch_stock_data(ticker_symbol, start_dt, end_dt, max_retries=3):
                # Optional: try Alpha Vantage CSV (free tier) if API key provided
                alpha_key = os.getenv('ALPHA_VANTAGE_KEY')
                if alpha_key:
                    try:
                        av_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker_symbol}&outputsize=full&apikey={alpha_key}&datatype=csv'
                        resp = requests.get(av_url, timeout=10)
                        if resp.status_code == 200 and len(resp.content) > 100:
                            try:
                                df_av = pd.read_csv(StringIO(resp.text), parse_dates=['timestamp'])
                                # AlphaVantage CSV uses 'timestamp' column; convert to Date index named 'Date'
                                df_av = df_av.rename(columns={'timestamp': 'Date'}).set_index('Date')
                                if not df_av.empty:
                                    # AlphaVantage columns differ; ensure 'Close' present
                                    if 'close' in df_av.columns:
                                        df_av = df_av.rename(columns={'close': 'Close'})
                                    return df_av
                            except Exception:
                                pass
                    except Exception:
                        pass
                # 1) Try yf.download
                try:
                    df_local = yf.download(ticker_symbol, start=start_dt, end=end_dt, progress=False)
                    if not df_local.empty:
                        return df_local
                except Exception:
                    pass

                # 2) Try Ticker.history
                try:
                    tk = yf.Ticker(ticker_symbol)
                    df_local = tk.history(start=start_dt, end=end_dt)
                    if not df_local.empty:
                        return df_local
                except Exception:
                    pass

                # 3) Try direct Yahoo CSV download with retries
                period1 = int(time.mktime(start_dt.timetuple()))
                period2 = int(time.mktime(end_dt.timetuple()))
                url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker_symbol}?period1={period1}&period2={period2}&interval=1d&events=history'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                }
                session = requests.Session()
                for attempt in range(1, max_retries + 1):
                    try:
                        resp = session.get(url, headers=headers, timeout=10)
                        if resp.status_code == 200 and len(resp.content) > 100:
                            try:
                                df_local = pd.read_csv(StringIO(resp.text), parse_dates=['Date'], index_col='Date')
                                if not df_local.empty:
                                    return df_local
                            except Exception:
                                pass
                        # If rate limited or unauthorized, break early to avoid wasted retries
                        if resp.status_code in (401, 403, 429):
                            break
                    except requests.RequestException:
                        pass
                    time.sleep(1 * attempt)

                # Nothing found
                return pd.DataFrame()

            now = datetime.now()
            start = datetime(now.year - 10, now.month, now.day)
            end = now

            cache_key = _cache_key(ticker, start, end)

            # Demo mode: force use of bundled Resources CSV (or TSLA.csv)
            if mode == 'demo':
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                resources_dir = os.path.join(base_dir, 'Resources')
                demo_candidates = [os.path.join(resources_dir, f'{ticker}.csv'), os.path.join(resources_dir, 'TSLA.csv')]
                df = pd.DataFrame()
                for demo_path in demo_candidates:
                    try:
                        if os.path.exists(demo_path):
                            demo_df = pd.read_csv(demo_path, parse_dates=['Date'], index_col='Date')
                            if not demo_df.empty:
                                df = demo_df.copy()
                                break
                    except Exception:
                        continue
                if df.empty:
                    return Response({'error': 'Demo data not found for the given ticker. Put a CSV in Resources or try a different ticker.'}, status=status.HTTP_404_NOT_FOUND)
            elif mode == 'cached':
                df = _load_cache(cache_key)
                if df is None or df.empty:
                    return Response(
                        {'error': 'No cached data found for this ticker. Run Live mode first to populate the cache.'},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                # live mode: cache-first, then remote providers; do not fall back to demo CSV automatically
                df = _load_cache(cache_key)
                if df is None or df.empty:
                    df = fetch_stock_data(ticker, start, end)
                    if not df.empty:
                        _save_cache(cache_key, df)
                if df is None or df.empty:
                    return Response({'error': 'No data found for the given ticker from remote provider. Try demo mode or a different ticker.'}, status=status.HTTP_404_NOT_FOUND)

            df = df.reset_index()

            # Generate Basic Plot
            plt.switch_backend('AGG')
            plt.figure(figsize=(9, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.title(ticker)
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()

            # Save Plot
            image_name = f'{ticker}_plot.png'
            plot_url = save_plot(image_name)

            # 100 days moving average
            df['MA_100'] = df['Close'].rolling(100).mean()
            plt.switch_backend('AGG')
            plt.figure(figsize=(9, 5))
            plt.plot(df.MA_100, 'r', label='100 DMA')
            plt.plot(df.Close, label='Closing Price')
            plt.title(f'100 Days Moving-Average - {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            
            # Save Plot
            image_100_name = f'{ticker}_100_dma.png'
            plot_100_url = save_plot(image_100_name)

            # 200 days moving average
            df['MA_200'] = df['Close'].rolling(200).mean()
            plt.figure(figsize=(9, 5))
            plt.plot(df['Close'], label='Closing Price')
            plt.plot(df['MA_100'], 'r', label='100 DMA')
            plt.plot(df['MA_200'], 'g', label='200 DMA')
            plt.title(f'200 Days Moving-Average - {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()

            # Save plot
            image_200_name = f'{ticker}_200_dma.png'
            plot_200_url = save_plot(image_200_name)

            # Percent change
            df['Percentage Change'] = df['Close'].pct_change()
            plt.figure(figsize=(9, 5))
            plt.plot(df['Percentage Change'])
            plt.title('Percent Change')

            # Save plot
            image_pctchange_name = f'{ticker}_pct.png'
            plot_pct_url = save_plot(image_pctchange_name)

            # Splitting data into training and testing datasets.
            training_df = pd.DataFrame(df['Close'][0:int(len(df)*0.7)])
            testing_df = pd.DataFrame(df['Close'][int(len(df)*0.7):len(df)])

            # Scaling down between 0 and 1
            scaler = MinMaxScaler(feature_range=(0, 1))

            # Try to load ML Model (optional). If `keras` isn't installed, skip predictions.
            try:
                from keras.models import load_model
                keras_available = True
            except Exception:
                keras_available = False

            # Preparing Test Data
            past_100_days = training_df.tail(100)
            final_df = pd.concat([past_100_days, testing_df], ignore_index=True)
            input_data = scaler.fit_transform(final_df)

            x_test = []
            y_test = []

            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i-100:i])
                y_test.append(input_data[i, 0])
            x_test, y_test = np.array(x_test), np.array(y_test)

            # Compute a simple baseline (persistence) prediction and metrics on original prices
            try:
                # y_true: actual prices corresponding to test period (use positional iloc to avoid column name issues)
                y_true = final_df.iloc[100:, 0].values.reshape(-1, 1)
            except Exception:
                y_true = np.array([]).reshape(-1, 1)

            baseline_mse = None
            baseline_rmse = None
            baseline_r2 = None
            if y_true.size:
                # naive prediction: previous day's price
                naive_preds = final_df.iloc[99:len(final_df)-1, 0].values.reshape(-1, 1)
                if len(naive_preds) == len(y_true):
                    baseline_mse = mean_squared_error(y_true, naive_preds)
                    baseline_rmse = np.sqrt(baseline_mse)
                    try:
                        baseline_r2 = r2_score(y_true, naive_preds)
                    except Exception:
                        baseline_r2 = None

            image_prediction_url = None
            mse = None
            rmse = None
            r2 = None
            # fields for explicit model vs baseline metrics
            model_mse = None
            model_rmse = None
            model_r2 = None
            baseline_mse = baseline_mse
            baseline_rmse = baseline_rmse
            baseline_r2 = baseline_r2

            # If no trained model available, use baseline metrics so UI shows values
            if not keras_available:
                mse = baseline_mse
                rmse = baseline_rmse
                r2 = baseline_r2

            if keras_available:
                try:
                    # Load model from absolute Resources path to avoid cwd issues
                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    model_path = os.path.join(base_dir, 'Resources', 'stock_prediction_model.keras')
                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model file not found: {model_path}")
                    model = load_model(model_path)
                    # Predictions
                    y_predicted = model.predict(x_test)

                    # revert scaled transform to original price
                    y_predicted = scaler.inverse_transform(y_predicted)
                    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
                    y_predicted = pd.DataFrame(y_predicted)
                    y_test = pd.DataFrame(y_test)

                    # Making Predictions
                    plt.figure(figsize=(9, 5))
                    plt.plot(y_test, 'r', label='Original Price')
                    plt.plot(y_predicted, 'g', label='Predicted Price')
                    plt.title(f'Prediction for - {ticker}')
                    plt.xlabel('Days')
                    plt.ylabel('Price')
                    plt.legend()

                    # Save predicted plot
                    image_prediction_name = f'{ticker}_prediction.png'
                    image_prediction_url = save_plot(image_prediction_name)

                    # Model Evaluation
                    # MSE, RMSE and r2_score (model)
                    model_mse = mean_squared_error(y_test, y_predicted)
                    model_rmse = np.sqrt(model_mse)
                    try:
                        model_r2 = r2_score(y_test, y_predicted)
                    except Exception:
                        model_r2 = None
                    # also set the legacy keys to model metrics
                    mse = model_mse
                    rmse = model_rmse
                    r2 = model_r2
                except Exception as model_exc:
                    # If model loading or prediction fails, log and return plots without prediction
                    tbm = traceback.format_exc()
                    print('Model load/predict error:', tbm)
                    image_prediction_url = None
                    # fall back to baseline if available
                    mse = baseline_mse
                    rmse = baseline_rmse
                    r2 = baseline_r2
                    model_mse = None
                    model_rmse = None
                    model_r2 = None

            return Response({
                'Success': 'Success',
                'plot': plot_url,
                'plot_100': plot_100_url,
                'plot_200': plot_200_url,
                'plot_pct': plot_pct_url,
                'prediction': image_prediction_url,
                # legacy keys (model if available, else baseline)
                'mse': mse,
                'rmse': rmse,
                'r2': r2,
                # explicit breakdown
                'baseline_mse': baseline_mse,
                'baseline_rmse': baseline_rmse,
                'baseline_r2': baseline_r2,
                'model_mse': model_mse,
                'model_rmse': model_rmse,
                'model_r2': model_r2,
            })
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            return Response({'error': 'Internal server error', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def demo_view(request, ticker):
    """Simple HTML demo page that shows generated media images for a ticker.
    If images are missing, instructs the user to POST to `/api/v1/predict/` to generate them.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    media_root = os.path.join(base_dir, 'backend-drf', 'media') if os.path.isdir(os.path.join(base_dir, 'backend-drf')) else os.path.join(base_dir, 'media')
    # Use settings.MEDIA_URL for URL prefix
    from django.conf import settings
    media_url = settings.MEDIA_URL

    files = {
        'plot': f'{ticker}_plot.png',
        'plot_100': f'{ticker}_100_dma.png',
        'plot_200': f'{ticker}_200_dma.png',
        'plot_pct': f'{ticker}_pct.png',
        'prediction': f'{ticker}_prediction.png',
    }

    parts = [f'<h1>Demo preview for {ticker}</h1>']
    any_present = False
    for key, name in files.items():
        path_on_disk = os.path.join(settings.MEDIA_ROOT, name)
        if os.path.exists(path_on_disk):
            any_present = True
            parts.append(f'<h3>{key}</h3><img src="{media_url}{name}" style="max-width:800px; width:100%"><br/>')

    if not any_present:
        parts.append('<p>No generated images found for this ticker.</p>')
        parts.append('<p>Call the prediction endpoint with a POST to <code>/api/v1/predict/</code> with JSON <code>{"ticker":"TSLA"}</code> to generate demo images.</p>')

    html = '\n'.join(parts)
    return HttpResponse(html)
