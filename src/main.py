import backtrader as bt
import pandas as pd
from datetime import datetime
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.strategies.ema_crossover_strategy import EMACrossoverStrategy
from src.data.data_loader import DataLoader
from src.analysis.backtest_analyzer import BacktestAnalyzer

def main():
    try:
        # 创建回测引擎
        cerebro = bt.Cerebro()
        
        # 加载数据
        data_loader = DataLoader()
        data = data_loader.load_data()
        cerebro.adddata(data)
        
        # 设置初始资金
        initial_cash = 1000000.0
        cerebro.broker.setcash(initial_cash)
        print(f'初始资金: {initial_cash:.2f}')
        
        # 设置手续费
        cerebro.broker.setcommission(commission=0.001)  # 0.1% 手续费
        
        # 添加策略
        cerebro.addstrategy(EMACrossoverStrategy)
        
        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # 运行回测
        results = cerebro.run()
        
        # 创建分析器实例
        analyzer = BacktestAnalyzer(cerebro, results, data)
        
        # 运行Buy&Hold策略对比
        analyzer.run_buy_and_hold(initial_cash)
        
        # 输出分析结果
        analyzer.print_analysis()
        
        # 打印最终资金
        final_cash = cerebro.broker.getvalue()
        print('最终资金: %.2f' % final_cash)
        
        # 绘制结果
        analyzer.plot_results()
    except Exception as e:
        print(f"回测过程出错: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    main() 