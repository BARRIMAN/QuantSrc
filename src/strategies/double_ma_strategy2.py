import backtrader as bt
import datetime

file_path = 'BTCUSDT_1d_2021_2025_data_cleaned.csv'


# ========== 策略1：双均线策略 ==========
class DoubleMAStrategy(bt.Strategy):
    params = (
        ('fast_period', 5),
        ('slow_period', 10),
    )

    def __init__(self):
        # 定义两条移动平均线
        self.fast_ma = bt.ind.SMA(self.datas[0].close, period=self.p.fast_period)
        self.slow_ma = bt.ind.SMA(self.datas[0].close, period=self.p.slow_period)
        # 侦测快慢均线交叉
        self.crossover = bt.ind.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        # 如果当前没持仓
        if not self.position:
            # 出现金叉，短均线刚上穿长均线 => 买入
            if self.crossover[0] > 0:
                # size = self.broker.get_cash() / self.datas[0].close[0]
                # self.buy(size=size)
                print(f"BUY SIGNAL! Date: {self.datas[0].datetime.date(0)}, Cash: {self.broker.get_cash()}, Price: {self.datas[0].close[0]}")
                self.buy()
        else:
            # 有持仓，出现死叉（短均线下穿长均线） => 卖出
            if self.crossover[0] < 0:
                # self.sell(size=self.position.size)
                self.sell()
                print(f"SELL SIGNAL! Date: {self.datas[0].datetime.date(0)}, Cash: {self.broker.get_cash()}, Price: {self.datas[0].close[0]}")
# ========== 策略2：Buy & Hold (对照组) ==========
class BuyHold(bt.Strategy):
    """
    启动后一次性买入并持有到结束，适合作为基准对照策略
    """
    def __init__(self):
        pass

    def next(self):
        # 第一次执行 next() 时，如果空仓，就全仓买入
        if not self.position:
            # size = self.broker.get_cash() / self.datas[0].close[0]
            self.buy()


def run_backtest(datafile = file_path):
    """执行回测，并对比 [双均线] vs [买入持有] 两种策略表现"""

    cerebro = bt.Cerebro()

    # ========== 1) 读取数据 ==========

    # 这里示例你的 CSV 日期格式是 "2021/01/01"，用 dtformat='%Y/%m/%d'
    data = bt.feeds.GenericCSVData(
        dataname=datafile,
        dtformat='%Y-%m-%d',  # 如果是"2021-01-01"，就改成'%Y-%m-%d'
        datetime=0,           # 第0列是日期
        time=-1,              # 无单独时间列
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        skiprows=1            # 跳过表头
    )
    cerebro.adddata(data)

    # ========== 2) 设置经纪商（账户）参数 ==========
    cerebro.broker.setcash(1000000.0)          # 初始资金：100 万
    cerebro.broker.setcommission(commission=0.001)  # 交易佣金：万分之10 (示例)

    # ========== 3) 添加两个策略 ==========
    # 第一个：双均线策略
    cerebro.addstrategy(DoubleMAStrategy, fast_period=5, slow_period=10)
    # 第二个：Buy & Hold 策略
    cerebro.addstrategy(BuyHold)

    # ========== 4) 添加分析器 ==========
    # - SharpeRatio: 夏普比率
    # - DrawDown:    最大回撤
    # - AnnualReturn:年化收益率 (按年度)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')

    # ========== 5) 执行回测 ==========
    print("=== Starting Portfolio Value: {:.2f} ===".format(cerebro.broker.getvalue()))
    results = cerebro.run()
    print("=== Final Portfolio Value: {:.2f} ===".format(cerebro.broker.getvalue()))

    # 因为添加了2个策略，所以 results 会返回一个长度为2的列表
    strat0 = results[0]  # DoubleMAStrategy
    strat1 = results[1]  # BuyHold

    # 读取各自的分析器
    drawdown0 = strat0.analyzers.drawdown.get_analysis()
    annual0   = strat0.analyzers.annual_return.get_analysis()

    sharpe1   = strat1.analyzers.sharpe.get_analysis()
    drawdown1 = strat1.analyzers.drawdown.get_analysis()
    annual1   = strat1.analyzers.annual_return.get_analysis()

    # ========== 6) 分别打印两种策略结果 ==========

    # ---- 双均线策略 ----
    print("\n===== [双均线策略] 业绩指标 =====")

    # 计算最大回撤
    if 'maxdrawdown' in drawdown0:
        print(f"Max DrawDown %: {drawdown0['maxdrawdown']:.2f}%")
    else:
        print("No drawdown data available.")

    # 计算夏普比率
    sharpe_ratio0 = strat0.analyzers.sharpe.get_analysis().get('sharperatio', None)
    if sharpe_ratio0 is not None:
        print(f"Sharpe Ratio: {sharpe_ratio0:.2f}")
    else:
        print("Sharpe Ratio: No trading activity.")

    # 处理年化收益率数据
    print(f"Annual Returns by Year: {annual0}")



    # ---- Buy & Hold 策略 ----
    print("\n===== [Buy & Hold] 业绩指标 =====")
    print(f"Sharpe Ratio: {sharpe1}")
    # print(f"Max DrawDown %: {drawdown1['maxdrawdown']:.2f}%")

    if 'maxdrawdown' in drawdown1:
        print(f"Max DrawDown %: {drawdown1['max']:.2f}%")
    else:
        print("No drawdown data available.")

    print(f"Annual Returns by Year: {annual1}")


    # ========== 7) 绘制图表(可选) ==========
    # 将在图中同时显示两条资金曲线、交易点等信息
    cerebro.plot()

if __name__ == '__main__':
    run_backtest()
