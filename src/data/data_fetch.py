import ccxt
import pandas as pd

okx = ccxt.okx()
bars = okx.fetch_ohlcv("BTC/USDT", timeframe="1d", limit=100)
df_okx = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
df_okx["timestamp"] = pd.to_datetime(df_okx["timestamp"], unit="ms")
print(df_okx.head())
