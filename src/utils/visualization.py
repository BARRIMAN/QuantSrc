"""
数据可视化工具
用于绘制价格和指标图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict

class DataVisualizer:
    @staticmethod
    def plot_price_and_volume(df: pd.DataFrame,
                             title: str = 'BTC/USDT Price and Volume',
                             save_path: Optional[str] = None) -> None:
        """
        绘制价格和成交量图表
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        title : str
            图表标题
        save_path : str, optional
            保存路径
        """
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.7, 0.3])

        # 添加K线图
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['open'],
                                    high=df['high'],
                                    low=df['low'],
                                    close=df['close'],
                                    name='OHLC'),
                     row=1, col=1)

        # 添加成交量
        colors = ['red' if row['close'] >= row['open'] else 'green' 
                 for _, row in df.iterrows()]
        
        fig.add_trace(go.Bar(x=df.index,
                           y=df['volume'],
                           name='Volume',
                           marker_color=colors),
                     row=2, col=1)

        # 更新布局
        fig.update_layout(
            title=title,
            yaxis_title='Price',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False
        )

        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
            
    @staticmethod
    def plot_technical_indicators(df: pd.DataFrame,
                                indicators: List[str],
                                title: str = 'Technical Indicators',
                                save_path: Optional[str] = None) -> None:
        """
        绘制技术指标图表
        
        Parameters:
        -----------
        df : pd.DataFrame
            价格数据
        indicators : List[str]
            要绘制的指标列表
        title : str
            图表标题
        save_path : str, optional
            保存路径
        """
        n_indicators = len(indicators)
        fig = make_subplots(rows=n_indicators + 1, cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           row_heights=[0.4] + [0.6/n_indicators] * n_indicators)

        # 添加价格
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['open'],
                                    high=df['high'],
                                    low=df['low'],
                                    close=df['close'],
                                    name='OHLC'),
                     row=1, col=1)

        # 添加技术指标
        for i, indicator in enumerate(indicators, 2):
            if indicator.startswith('sma_'):
                period = indicator.split('_')[1]
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df[indicator],
                                       name=f'SMA {period}',
                                       line=dict(width=1)),
                            row=i, col=1)
            elif indicator.startswith('ema_'):
                period = indicator.split('_')[1]
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df[indicator],
                                       name=f'EMA {period}',
                                       line=dict(width=1)),
                            row=i, col=1)
            elif indicator == 'rsi':
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['rsi'],
                                       name='RSI',
                                       line=dict(width=1)),
                            row=i, col=1)
                # 添加RSI的超买超卖线
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=i, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=i, col=1)
            elif indicator == 'macd':
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['macd'],
                                       name='MACD',
                                       line=dict(width=1)),
                            row=i, col=1)
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['macd_signal'],
                                       name='Signal',
                                       line=dict(width=1)),
                            row=i, col=1)
                fig.add_trace(go.Bar(x=df.index,
                                   y=df['macd_hist'],
                                   name='Histogram'),
                            row=i, col=1)
            elif indicator == 'bollinger_bands':
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['bb_upper'],
                                       name='Upper Band',
                                       line=dict(width=1)),
                            row=i, col=1)
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['bb_middle'],
                                       name='Middle Band',
                                       line=dict(width=1)),
                            row=i, col=1)
                fig.add_trace(go.Scatter(x=df.index,
                                       y=df['bb_lower'],
                                       name='Lower Band',
                                       line=dict(width=1)),
                            row=i, col=1)

        # 更新布局
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            height=300 * (n_indicators + 1)
        )

        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
            
    @staticmethod
    def plot_correlation_heatmap(df: pd.DataFrame,
                               columns: Optional[List[str]] = None,
                               title: str = 'Correlation Heatmap',
                               save_path: Optional[str] = None) -> None:
        """
        绘制相关性热力图
        
        Parameters:
        -----------
        df : pd.DataFrame
            数据
        columns : List[str], optional
            要计算相关性的列
        title : str
            图表标题
        save_path : str, optional
            保存路径
        """
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
            
        corr = df[columns].corr()
        
        plt.figure(figsize=(12, 8))
        plt.imshow(corr, cmap='coolwarm', aspect='auto')
        plt.colorbar()
        
        # 添加相关系数标签
        for i in range(len(columns)):
            for j in range(len(columns)):
                plt.text(j, i, f'{corr.iloc[i, j]:.2f}',
                        ha='center', va='center')
                
        plt.xticks(range(len(columns)), columns, rotation=45)
        plt.yticks(range(len(columns)), columns)
        plt.title(title)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show() 