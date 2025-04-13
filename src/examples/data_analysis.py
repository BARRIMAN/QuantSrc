"""
数据分析和可视化示例
展示数据加载、指标计算和可视化的使用方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_loader import DataLoader
from utils.technical_indicators import TechnicalIndicators
from utils.visualization import DataVisualizer

def main():
    # 初始化数据加载器
    loader = DataLoader()
    
    # 加载数据
    df = loader.get_data()
    
    # 计算技术指标
    df = TechnicalIndicators.add_sma(df)
    df = TechnicalIndicators.add_ema(df)
    df = TechnicalIndicators.add_rsi(df)
    df = TechnicalIndicators.add_macd(df)
    df = TechnicalIndicators.add_bollinger_bands(df)
    df = TechnicalIndicators.add_atr(df)
    
    # 绘制价格和成交量图表
    DataVisualizer.plot_price_and_volume(df)
    
    # 绘制技术指标图表
    indicators = ['sma_20', 'sma_50', 'rsi', 'macd', 'bollinger_bands']
    DataVisualizer.plot_technical_indicators(df, indicators)
    
    # 绘制相关性热力图
    columns = ['close', 'volume', 'rsi', 'macd', 'atr']
    DataVisualizer.plot_correlation_heatmap(df, columns)
    
    # 打印基本统计信息
    print("\n基本统计信息:")
    print(df[['close', 'volume', 'rsi', 'macd', 'atr']].describe())
    
    # 计算一些基本的交易统计
    print("\n交易统计:")
    print(f"总交易日数: {len(df)}")
    print(f"平均日成交量: {df['volume'].mean():.2f}")
    print(f"平均日波动率: {df['atr'].mean():.2f}")
    print(f"最高价: {df['high'].max():.2f}")
    print(f"最低价: {df['low'].min():.2f}")
    print(f"当前价格: {df['close'].iloc[-1]:.2f}")
    
    # 计算一些技术指标统计
    print("\n技术指标统计:")
    print(f"RSI超买天数: {(df['rsi'] > 70).sum()}")
    print(f"RSI超卖天数: {(df['rsi'] < 30).sum()}")
    print(f"MACD金叉次数: {(df['macd'] > df['macd_signal']).sum()}")
    print(f"MACD死叉次数: {(df['macd'] < df['macd_signal']).sum()}")

if __name__ == '__main__':
    main() 