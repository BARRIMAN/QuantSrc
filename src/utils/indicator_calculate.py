import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib  

# 1. 读取数据
df = pd.read_csv('BTCUSDT_1d_2021_2025_cleaned.csv')

# 移动平均线
df['MA_20'] = talib.SMA(df['Close'], timeperiod=20)

# 布林带 (talib.BBANDS)
upper, middle, lower = talib.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2)
df['Bollinger_Upper'] = upper
df['Bollinger_Middle'] = middle
df['Bollinger_Lower'] = lower

# RSI
df['RSI_14'] = talib.RSI(df['Close'], timeperiod=14)


# MA20
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Close'], label='Close Price')
plt.plot(df.index, df['MA_20'], label='MA 20')
plt.title('BTC Price & MA_20')
plt.legend()
plt.show()


# Bollinger Bands
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Close'], label='Close')
plt.plot(df.index, df['Bollinger_Upper'], label='Upper Band', )
plt.plot(df.index, df['Bollinger_Middle'], label='Middle Band')
plt.plot(df.index, df['Bollinger_Lower'], label='Lower Band')
plt.title('BTC Price & Bollinger Bands')
plt.legend()
plt.show()

# RSI
plt.figure(figsize=(10, 4))
plt.plot(df.index, df['RSI_14'], label='RSI_14')
plt.axhline(30, color='gray', linestyle='--', label='OverSold 30')
plt.axhline(70, color='gray', linestyle='--', label='OverBought 70')
plt.title('RSI 14')
plt.legend()
plt.show()





