import backtrader as bt

class BuyAndHoldStrategy(bt.Strategy):
    """
    Buy & Hold 策略
    在回测开始时买入全部仓位，在回测结束时卖出
    """
    def __init__(self):
        """
        初始化策略
        """
        self.order = None
        self.bought = False
        self.dataclose = self.datas[0].close
        
    def log(self, txt, dt=None):
        """
        日志函数
        """
        dt = dt or self.data.datetime.date(0)
        print(f'[Buy&Hold] {dt.isoformat()} {txt}')
        
    def next(self):
        """
        策略核心逻辑
        """
        # 如果已经有订单或已经买入，不执行操作
        if self.order or self.bought:
            return
            
        # 在第一个bar买入全部仓位
        if len(self) == 1:  # 第一个交易日
            available_cash = self.broker.getcash()
            current_price = self.dataclose[0]
            size = available_cash / current_price * 0.95  # 留5%作为手续费缓冲
            
            self.log(f'买入信号: 价格: {current_price:.2f}, 数量: {size:.3f}')
            self.order = self.buy(size=size)
            
        # 在最后一个bar卖出全部仓位
        if len(self) == len(self.data) - 1:  # 最后一个交易日
            if self.position:
                self.log(f'卖出信号: 价格: {self.dataclose[0]:.2f}, 持仓: {self.position.size:.3f}')
                self.order = self.sell(size=self.position.size)
                
    def notify_order(self, order):
        """
        订单状态更新通知
        """
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.bought = True
                self.log(
                    f'买入执行: 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.3f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
            else:
                self.log(
                    f'卖出执行: 价格: {order.executed.price:.2f}, '
                    f'数量: {order.executed.size:.3f}, '
                    f'成本: {order.executed.value:.2f}, '
                    f'手续费: {order.executed.comm:.2f}'
                )
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单取消/拒绝/资金不足: {order.status}')
            
        self.order = None 