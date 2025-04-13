"""
数据加载器基类
用于处理数据加载和基本预处理
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Union, List
import logging
import backtrader as bt
import os
from datetime import datetime

class DataLoader:
    """
    数据加载器
    """
    def __init__(self):
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建数据文件的绝对路径
        self.data_path = os.path.join(current_dir, 'BTCUSDT_1d_2021_2025_cleaned.csv')
        
    def load_data(self):
        """
        加载数据
        
        Returns:
        --------
        bt.feeds.PandasData
            backtrader可用的数据对象
        """
        # 检查数据文件是否存在
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"找不到数据文件: {self.data_path}")
            
        # 读取CSV文件
        df = pd.read_csv(self.data_path)
        
        # 重命名列以匹配backtrader的要求
        df.rename(columns={
            'Open time': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # 转换日期列
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        # 创建backtrader数据源
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为日期
            open='open',    # 使用重命名后的列名
            high='high',
            low='low',
            close='close',
            volume='volume',
            openinterest=-1 # 不使用持仓量
        )
        
        return data

    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        加载CSV文件
        
        Parameters:
        -----------
        filename : str
            CSV文件名
            
        Returns:
        --------
        pd.DataFrame
            加载的数据
        """
        try:
            file_path = self.data_dir / filename
            df = pd.read_csv(file_path)
            self.logger.info(f"成功加载数据文件: {filename}")
            return df
        except Exception as e:
            self.logger.error(f"加载数据文件失败: {filename}, 错误: {str(e)}")
            raise
            
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
            
        Returns:
        --------
        pd.DataFrame
            处理后的数据
        """
        # 确保日期列格式正确
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
        # 确保数值列格式正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # 删除缺失值
        df.dropna(inplace=True)
        
        # 按时间排序
        df.sort_index(inplace=True)
        
        return df
        
    def get_data(self, filename: str = 'BTCUSDT_1d_2021_2025_cleaned.csv') -> pd.DataFrame:
        """
        获取并预处理数据
        
        Parameters:
        -----------
        filename : str
            数据文件名
            
        Returns:
        --------
        pd.DataFrame
            处理后的数据
        """
        df = self.load_csv(filename)
        return self.preprocess_data(df)
        
    def get_data_range(self, 
                      df: pd.DataFrame,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取指定时间范围的数据
        
        Parameters:
        -----------
        df : pd.DataFrame
            原始数据
        start_date : str, optional
            开始日期，格式：'YYYY-MM-DD'
        end_date : str, optional
            结束日期，格式：'YYYY-MM-DD'
            
        Returns:
        --------
        pd.DataFrame
            指定时间范围的数据
        """
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df.index >= start_date]
            
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df.index <= end_date]
            
        return df 

    @staticmethod
    def load_crypto_data(file_path):
        """
        加载加密货币数据
        
        Parameters:
        -----------
        file_path : str
            CSV文件路径
            
        Returns:
        --------
        bt.feeds.PandasData
            backtrader数据源对象
        """
        # 读取CSV文件
        df = pd.read_csv(file_path)
        df['Open time'] = pd.to_datetime(df['Open time'])
        df.set_index('Open time', inplace=True)
        
        # 创建backtrader数据源
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为日期
            open=1,         # 使用第2列作为开盘价
            high=2,         # 使用第3列作为最高价
            low=3,          # 使用第4列作为最低价
            close=4,        # 使用第5列作为收盘价
            volume=5,       # 使用第6列作为成交量
            openinterest=-1 # 不使用持仓量
        )
        
        return data 