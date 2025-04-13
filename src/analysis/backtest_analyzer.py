import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime
import backtrader as bt
from strategies.buy_and_hold_strategy import BuyAndHoldStrategy

class BacktestAnalyzer:
    """
    回测结果分析器
    """
    def __init__(self, cerebro, results, data):
        """
        初始化分析器
        
        Parameters:
        -----------
        cerebro : bt.Cerebro
            回测引擎实例
        results : list
            回测结果列表
        data : bt.feeds.DataBase
            回测数据，用于Buy&Hold对比
        """
        self.cerebro = cerebro
        self.results = results[0]  # 获取第一个策略实例的结果
        self.data = data
        self.bh_results = None  # Buy&Hold策略结果
        
    def run_buy_and_hold(self, initial_cash):
        """
        运行Buy&Hold策略
        
        Parameters:
        -----------
        initial_cash : float
            初始资金
        """
        # 创建新的回测引擎
        cerebro = bt.Cerebro()
        
        # 添加数据
        cerebro.adddata(self.data)
        
        # 设置初始资金
        cerebro.broker.setcash(initial_cash)
        
        # 设置手续费
        cerebro.broker.setcommission(commission=0.001)
        
        # 添加Buy&Hold策略
        cerebro.addstrategy(BuyAndHoldStrategy)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # 运行回测
        results = cerebro.run()
        self.bh_results = results[0]
        
    def _get_strategy_metrics(self, results):
        """
        获取策略指标
        
        Parameters:
        -----------
        results : bt.Strategy
            策略结果
            
        Returns:
        --------
        dict
            策略指标字典
        """
        metrics = {}
        
        try:
            # 获取夏普率
            sharpe = results.analyzers.sharpe.get_analysis()
            metrics['sharpe_ratio'] = sharpe.get('sharperatio', 0.0)
            
            # 获取收益率
            returns = results.analyzers.returns.get_analysis()
            metrics['total_return'] = returns.get('rtot', 0.0) * 100
            metrics['annual_return'] = returns.get('rnorm100', 0.0)
            
            # 获取最大回撤
            drawdown = results.analyzers.drawdown.get_analysis()
            metrics['max_drawdown'] = drawdown.get('max', {}).get('drawdown', 0.0)
            
            # 获取最终资金
            metrics['final_value'] = results.broker.get_value()
            
        except Exception as e:
            print(f"获取策略指标失败: {str(e)}")
            # 设置默认值
            metrics = {
                'sharpe_ratio': 0.0,
                'total_return': 0.0,
                'annual_return': 0.0,
                'max_drawdown': 0.0,
                'final_value': 0.0
            }
            
        return metrics
        
    def print_analysis(self):
        """
        打印回测分析结果
        """
        try:
            # 获取策略指标
            strategy_metrics = self._get_strategy_metrics(self.results)
            
            # 输出回测指标
            print('\n=== 策略绩效分析 ===')
            print(f'总收益率: {strategy_metrics["total_return"]:.2f}%')
            print(f'年化收益率: {strategy_metrics["annual_return"]:.2f}%')
            print(f'最大回撤: {strategy_metrics["max_drawdown"]:.2f}%')
            print(f'夏普比率: {strategy_metrics["sharpe_ratio"]:.2f}')
            print(f'最终资金: {strategy_metrics["final_value"]:.2f}')
            
            # 运行Buy&Hold策略并获取结果
            if self.bh_results is None:
                self.run_buy_and_hold(self.cerebro.broker.startingcash)
                
            bh_metrics = self._get_strategy_metrics(self.bh_results)
            
            print('\n=== Buy & Hold 策略对比 ===')
            print(f'总收益率: {strategy_metrics["total_return"]:.2f}% vs {bh_metrics["total_return"]:.2f}%')
            print(f'年化收益率: {strategy_metrics["annual_return"]:.2f}% vs {bh_metrics["annual_return"]:.2f}%')
            print(f'最大回撤: {strategy_metrics["max_drawdown"]:.2f}% vs {bh_metrics["max_drawdown"]:.2f}%')
            print(f'夏普比率: {strategy_metrics["sharpe_ratio"]:.2f} vs {bh_metrics["sharpe_ratio"]:.2f}')
            print(f'最终资金: {strategy_metrics["final_value"]:.2f} vs {bh_metrics["final_value"]:.2f}')
            
            # 计算超额收益
            excess_return = strategy_metrics["annual_return"] - bh_metrics["annual_return"]
            print(f'\n超额收益: {excess_return:.2f}%')
            
            # 获取交易分析
            trade_analysis = self.results.analyzers.trades.get_analysis()
            
            print('\n=== 交易统计 ===')
            # 统计总交易次数
            total_trades = trade_analysis.get('total', {}).get('total', 0)
            print('总交易次数:', total_trades)
            
            if total_trades == 0:
                return
                
            # 统计盈利交易
            won = trade_analysis.get('won', {})
            won_trades = won.get('total', 0)
            print('盈利交易:', won_trades)
            if won_trades > 0:
                print('平均盈利: %.2f' % won.get('pnl', {}).get('average', 0.0))
                print('最大盈利: %.2f' % won.get('pnl', {}).get('max', 0.0))
                
            # 统计亏损交易
            lost = trade_analysis.get('lost', {})
            lost_trades = lost.get('total', 0)
            print('亏损交易:', lost_trades)
            if lost_trades > 0:
                print('平均亏损: %.2f' % lost.get('pnl', {}).get('average', 0.0))
                print('最大亏损: %.2f' % lost.get('pnl', {}).get('min', 0.0))
            
            # 计算胜率
            win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
            print('胜率: %.2f%%' % win_rate)
            
        except Exception as e:
            print(f"结果分析失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
    def plot_results(self):
        """
        绘制回测结果图表
        """
        try:
            # 使用 backtrader 默认的绘图方式
            self.cerebro.plot(style='candlestick', barup='green', bardown='red',
                            volup='green', voldown='red',
                            grid=True, volume=True)
        except Exception as e:
            print(f"绘图出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
    def get_performance_metrics(self):
        """
        获取性能指标
        
        Returns:
        --------
        dict
            包含各项性能指标的字典
        """
        trade_analysis = self.results.analyzers.trades.get_analysis()
        
        metrics = {
            'sharpe_ratio': self.results.analyzers.sharpe.get_analysis()['sharperatio'],
            'annual_return': self.results.analyzers.returns.get_analysis()['rnorm100'],
            'max_drawdown': self.results.analyzers.drawdown.get_analysis()['max']['drawdown'],
            'trade_analysis': trade_analysis,
        }
        
        # 添加胜率
        if 'total' in trade_analysis and trade_analysis['total']['total'] > 0:
            if 'won' in trade_analysis:
                metrics['win_rate'] = trade_analysis['won']['total'] / trade_analysis['total']['total'] * 100
            else:
                metrics['win_rate'] = 0
        else:
            metrics['win_rate'] = 0
            
        return metrics 