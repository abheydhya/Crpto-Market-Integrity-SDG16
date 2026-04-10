import ccxt
import pandas as pd
import numpy as np

def fetch_and_analyze(symbol='XRP/USDT', timeframe='1m', limit=100):
    # Initialize Binance connection
    exchange = ccxt.binance({'enableRateLimit': True})
    
    print(f"Fetching last {limit} minutes of {symbol} data...\n")
    # Fetch OHLCV (Open, High, Low, Close, Volume) data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    # Convert to a Pandas DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    print("Calculating statistical anomalies (Z-Score on Volume)...")
    
    # 1. Calculate the global average and standard deviation across all candles
    vol_mean = df['volume'].mean()
    vol_std = df['volume'].std()
    
    # 2. Calculate the Z-Score: (Current Volume - Average) / Standard Deviation
    df['vol_mean'] = vol_mean
    df['vol_std'] = vol_std
    df['z_score'] = (df['volume'] - vol_mean) / vol_std
    
    # 3. Define our threshold (Z-score > 3 is statistically highly unusual)
    threshold = 3.0
    df['is_anomaly'] = df['z_score'] > threshold
    
    # 4. Filter to see if any anomalies happened recently
    anomalies = df[df['is_anomaly']]
    
    if anomalies.empty:
        print("\n🟢 Market looks normal. No anomalies detected in this timeframe.")
    else:
        print(f"\n🚨 ALERT: Found {len(anomalies)} volume anomalies! Potential manipulation.")
        print(anomalies[['timestamp', 'close', 'volume', 'z_score']].to_string(index=False))

    return df

if __name__ == "__main__":
    fetch_and_analyze()