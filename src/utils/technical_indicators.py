"""
技术指标计算器
包含常用的技术分析指标
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List

class TechnicalIndicators:
    @staticmethod
    def add_sma(df: pd.DataFrame, 
                price_col: str = 'close',
                periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
        """
        添加简单移动平均线
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        price_col : str
            价格列名
        periods : List[int]
            移动平均周期列表
            
        Returns:
        --------
        pd.DataFrame
            添加了SMA的数据
        """
        for period in periods:
            df[f'sma_{period}'] = df[price_col].rolling(window=period).mean()
        return df
        
    @staticmethod
    def add_ema(df: pd.DataFrame,
                price_col: str = 'close',
                periods: List[int] = [12, 26]) -> pd.DataFrame:
        """
        添加指数移动平均线
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        price_col : str
            价格列名
        periods : List[int]
            移动平均周期列表
            
        Returns:
        --------
        pd.DataFrame
            添加了EMA的数据
        """
        for period in periods:
            df[f'ema_{period}'] = df[price_col].ewm(span=period, adjust=False).mean()
        return df
        
    @staticmethod
    def add_rsi(df: pd.DataFrame,
                price_col: str = 'close',
                period: int = 14) -> pd.DataFrame:
        """
        添加相对强弱指标(RSI)
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        price_col : str
            价格列名
        period : int
            RSI周期
            
        Returns:
        --------
        pd.DataFrame
            添加了RSI的数据
        """
        delta = df[price_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
        
    @staticmethod
    def add_macd(df: pd.DataFrame,
                 price_col: str = 'close',
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int = 9) -> pd.DataFrame:
        """
        添加MACD指标
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        price_col : str
            价格列名
        fast_period : int
            快线周期
        slow_period : int
            慢线周期
        signal_period : int
            信号线周期
            
        Returns:
        --------
        pd.DataFrame
            添加了MACD的数据
        """
        # 计算快线和慢线的EMA
        fast_ema = df[price_col].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df[price_col].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线
        df['macd'] = fast_ema - slow_ema
        
        # 计算信号线
        df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        
        # 计算MACD柱状图
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df
        
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame,
                           price_col: str = 'close',
                           period: int = 20,
                           std_dev: float = 2.0) -> pd.DataFrame:
        """
        添加布林带
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        price_col : str
            价格列名
        period : int
            移动平均周期
        std_dev : float
            标准差倍数
            
        Returns:
        --------
        pd.DataFrame
            添加了布林带的数据
        """
        # 计算中轨（简单移动平均线）
        df['bb_middle'] = df[price_col].rolling(window=period).mean()
        
        # 计算标准差
        rolling_std = df[price_col].rolling(window=period).std()
        
        # 计算上轨和下轨
        df['bb_upper'] = df['bb_middle'] + (rolling_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (rolling_std * std_dev)
        
        return df
        
    @staticmethod
    def add_atr(df: pd.DataFrame,
                period: int = 14) -> pd.DataFrame:
        """
        添加平均真实波幅(ATR)
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        period : int
            ATR周期
            
        Returns:
        --------
        pd.DataFrame
            添加了ATR的数据
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR
        df['atr'] = tr.rolling(window=period).mean()
        
        return df 