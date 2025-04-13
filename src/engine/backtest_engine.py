import backtrader as bt
from typing import Type, Union, Dict, Any

class BacktestEngine:
    """
    回测引擎类
    """
    def __init__(self, 
                 initial_cash: float = 1000000.0,
                 commission: float = 0.001):
        """
        初始化回测引擎
        
        Parameters:
        -----------
        initial_cash : float
            初始资金
        commission : float
            交易手续费率
        """
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
    def add_data(self, data):
        """
        添加数据源
        
        Parameters:
        -----------
        data : bt.feeds.PandasData
            backtrader数据源对象
        """
        self.cerebro.adddata(data)
        
    def add_strategy(self, strategy_class: Type[bt.Strategy], 
                    strategy_params: Dict[str, Any] = None):
        """
        添加策略
        
        Parameters:
        -----------
        strategy_class : Type[bt.Strategy]
            策略类
        strategy_params : Dict[str, Any], optional
            策略参数字典
        """
        if strategy_params:
            self.cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            self.cerebro.addstrategy(strategy_class)
            
    def run(self):
        """
        运行回测
        
        Returns:
        --------
        tuple
            (回测引擎实例, 回测结果)
        """
        print('初始资金: %.2f' % self.cerebro.broker.getvalue())
        results = self.cerebro.run()
        print('最终资金: %.2f' % self.cerebro.broker.getvalue())
        
        return self.cerebro, results 