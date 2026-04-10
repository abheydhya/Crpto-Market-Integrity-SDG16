import ccxt
import pandas as pd
import time

def fetch_live_data(symbol='XRP/USDT'):
    # Initialize the Binance exchange (no API keys needed for public data)
    exchange = ccxt.binance({
        'enableRateLimit': True, 
    })

    try:
        print(f"Connecting to Binance to fetch {symbol} data...\n")
        
        # 1. Fetch the Order Book (The liquidity depth)
        order_book = exchange.fetch_order_book(symbol, limit=5)
        bids = order_book['bids'] # People waiting to buy
        asks = order_book['asks'] # People waiting to sell
        
        print("--- LIVE ORDER BOOK (Top 5) ---")
        print(f"Highest Bid (Buy): {bids[0][0]} USDT | Volume: {bids[0][1]}")
        print(f"Lowest Ask (Sell): {asks[0][0]} USDT | Volume: {asks[0][1]}\n")

        # 2. Fetch Recent Trades (The actual executed market action)
        trades = exchange.fetch_trades(symbol, limit=5)
        
        # Convert to a Pandas DataFrame for easy math later
        df_trades = pd.DataFrame(trades)
        
        # Clean up the dataframe to only show what we care about
        df_cleaned = df_trades[['datetime', 'side', 'price', 'amount']]
        
        print("--- MOST RECENT TRADES ---")
        print(df_cleaned.to_string(index=False))
        print("\nPipeline check successful. Data stream is active.")
        
        return df_cleaned

    except Exception as e:
        print(f"Error fetching data: {e}")

# Run the function if we execute this script
if __name__ == "__main__":
    fetch_live_data()