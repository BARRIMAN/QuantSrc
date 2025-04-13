import backtrader as bt
import numpy as np

class EmaRsiStrategy(bt.Strategy):
    """
    EMA交叉结合RSI的交易策略
    增加了成交量过滤和资金管理
    """
    params = (
        ('ema1_period', 12),     # 短期EMA周期
        ('ema2_period', 26),     # 长期EMA周期
        ('rsi_period', 14),      # RSI周期
        ('rsi_threshold', 50),   # RSI阈值
        ('volume_period', 20),   # 成交量均线周期
        ('risk_ratio', 0.02),    # 单次交易风险比例
        ('atr_period', 14),      # ATR周期
    )

    def __init__(self):
        # 保存收盘价和成交量的引用
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume
        
        # 创建技术指标
        # EMA指标
        self.ema1 = bt.indicators.ExponentialMovingAverage(
            self.dataclose, period=self.params.ema1_period)
        self.ema2 = bt.indicators.ExponentialMovingAverage(
            self.dataclose, period=self.params.ema2_period)
        
        # RSI指标
        self.rsi = bt.indicators.RSI(
            self.dataclose, period=self.params.rsi_period)
        
        # 成交量指标
        self.volume_ma = bt.indicators.SMA(
            self.datavolume, period=self.params.volume_period)
        
        # ATR指标用于计算止损
        self.atr = bt.indicators.ATR(
            self.data, period=self.params.atr_period)
        
        # 创建交叉信号
        self.crossover = bt.indicators.CrossOver(self.ema1, self.ema2)
        
        # 用于跟踪订单和止损
        self.order = None
        self.stop_price = None
        self.position_size = 0
        
        # 用于记录交易
        self.trades = []
        self.trade_dates = []

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行: 价格: {order.executed.price:.2f}, 数量: {order.executed.size:.3f}, '
                      f'成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
                # 设置止损价格
                self.stop_price = order.executed.price - self.atr[0] * 2
                self.position_size = order.executed.size
            else:
                self.log(f'卖出执行: 价格: {order.executed.price:.2f}, 数量: {order.executed.size:.3f}, '
                      f'成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
                # 清除止损价格
                self.stop_price = None
                self.position_size = 0

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.trades.append(trade.pnl)
        self.trade_dates.append(self.data.datetime.date(0))
        self.log(f'交易利润: 毛利润 {trade.pnl:.2f}, 净利润 {trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def get_position_size(self):
        """计算基于风险的仓位大小"""
        # 计算每笔交易的风险金额
        risk_amount = self.broker.getvalue() * self.params.risk_ratio
        # 使用ATR作为止损距离
        stop_distance = self.atr[0] * 2
        # 计算合适的仓位大小
        if stop_distance > 0:
            size = risk_amount / stop_distance
            # 确保size不为0且不超过账户价值的50%
            max_size = self.broker.getvalue() * 0.5 / self.dataclose[0]
            return min(max(0.001, size), max_size)
        return 0.001

    def next(self):
        # 如果有待处理的订单，不执行任何操作
        if self.order:
            return

        # 成交量过滤：当前成交量必须高于均线
        volume_filter = self.datavolume[0] > self.volume_ma[0]

        # 如果没有持仓
        if not self.position:
            # 开仓条件：
            # 1. EMA金叉
            # 2. RSI > 阈值
            # 3. 成交量放大
            if (self.crossover > 0 and 
                self.rsi > self.params.rsi_threshold and 
                volume_filter):
                
                # 计算仓位大小
                size = self.get_position_size()
                
                # 记录买入信号
                self.log(f'买入信号: 价格: {self.dataclose[0]:.2f}, 数量: {size:.3f}')
                
                # 执行买入
                self.order = self.buy(size=size)

        # 如果持有多头仓位
        else:
            # 平仓条件：
            # 1. EMA死叉且RSI < 阈值且成交量放大
            # 2. 或者触及止损
            hit_stop_loss = (self.stop_price is not None and 
                           self.dataclose[0] < self.stop_price)
            
            if ((self.crossover < 0 and 
                 self.rsi < self.params.rsi_threshold and 
                 volume_filter) or hit_stop_loss):
                
                self.log(f'卖出信号: {self.dataclose[0]:.2f}')
                # 确保卖出数量与持仓数量相同
                self.order = self.sell(size=self.position_size) 