import backtrader as bt

class EMACrossoverStrategy(bt.Strategy):
    """
    EMA交叉策略
    """
    params = (
        ('ema1_period', 12),  # 短期EMA周期
        ('ema2_period', 26),  # 长期EMA周期
        ('volume_period', 20),  # 成交量均线周期
        ('position_size', 0.95),  # 仓位大小比例
    )

    def __init__(self):
        """
        初始化策略
        """
        # 计算技术指标
        self.ema1 = bt.indicators.EMA(self.data.close, period=self.params.ema1_period)
        self.ema2 = bt.indicators.EMA(self.data.close, period=self.params.ema2_period)
        
        # 将成交量均线添加到成交量子图
        self.volume_ma = bt.indicators.SMA(self.data.volume, period=self.params.volume_period,
                                         subplot=True)  # 添加subplot=True参数
        
        # 交叉信号
        self.crossover = bt.indicators.CrossOver(self.ema1, self.ema2)
        
        # 记录交易状态
        self.order = None
        self.position_size = []  # 用于记录持仓大小
        self.buyprice = 0
        self.buycomm = 0
        self.bar_executed = 0
        
    def log(self, txt, dt=None):
        """
        日志函数
        """
        dt = dt or self.data.datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        
    def next(self):
        """
        策略核心逻辑
        """
        # 如果已经有订单，不执行新的交易
        if self.order:
            return
            
        # 获取当前持仓
        position_size = self.position.size if self.position else 0
        
        # 计算可用资金（考虑手续费和保证金）
        available_cash = self.broker.getcash()
        commission_rate = 0.001  # 0.1% 手续费
        margin_requirement = 1.1  # 10% 保证金要求
        
        # 计算EMA
        ema12 = self.ema1[0]
        ema26 = self.ema2[0]
        
        # 记录当前价格
        current_price = self.data.close[0]
        
        # 买入信号：EMA12上穿EMA26
        if not position_size and ema12 > ema26 and self.ema1[-1] <= self.ema2[-1]:
            # 计算可买入的数量（考虑手续费和保证金）
            max_size = (available_cash / margin_requirement) / (current_price * (1 + commission_rate))
            size = max_size * 0.95  # 留5%的缓冲
            self.log(f'买入信号: 价格: {current_price:.2f}, 数量: {size:.3f}, 可用资金: {available_cash:.2f}')
            self.order = self.buy(size=size)
            
        # 卖出信号：EMA12下穿EMA26
        elif position_size > 0 and ema12 < ema26 and self.ema1[-1] >= self.ema2[-1]:
            self.log(f'卖出信号: 价格: {current_price:.2f}, 持仓: {position_size:.3f}')
            self.order = self.sell(size=position_size)  # 卖出全部持仓
        
    def notify_order(self, order):
        """
        订单状态更新通知
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交或已接受，等待执行
            return
            
        # 检查订单是否已完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.log(
                    f'买入执行: 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.3f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
                self.bar_executed = len(self)
                
            else:  # 卖出
                cost = self.buyprice * order.executed.size
                profit_gross = order.executed.price * order.executed.size - cost
                profit_net = profit_gross - order.executed.comm - self.buycomm
                
                self.log(
                    f'卖出执行: 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.3f}, '
                    f'成本: {cost:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
                
                self.log(f'交易利润: 毛利润 {profit_gross:.2f}, 净利润 {profit_net:.2f}')
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单取消/拒绝/资金不足: {order.status}')
            
        # 重置订单
        self.order = None
        
    def notify_trade(self, trade):
        """
        交易结果通知
        """
        if not trade.isclosed:
            return
            
        self.log(f'交易利润: 毛利润 {trade.pnl:.2f}, 净利润 {trade.pnlcomm:.2f}') 