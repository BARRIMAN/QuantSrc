import backtrader as bt
import datetime
import pandas as pd

class DoubleMAStrategy(bt.Strategy):
    params = (
        ('fast_period', 20),
        ('slow_period', 50),
    )

    def __init__(self):
        self.fast_ma = bt.ind.SMA(self.datas[0].close, period=self.params.fast_period)
        self.slow_ma = bt.ind.SMA(self.datas[0].close, period=self.params.slow_period)
        self.crossover = bt.ind.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):

        # print(f"当前日期: {self.datas[0].datetime.date(0)}, 收盘价: {self.datas[0].close[0]}")

        if not self.position:
            if self.crossover[0] > 0:
                print(f"BUY SIGNAL! Date: {self.datas[0].datetime.date(0)}, Cash: {self.broker.get_cash()}, Price: {self.datas[0].close[0]}")
                self.buy()
        else:
            if self.crossover[0] < 0:
                self.sell()
                print(f"SELL SIGNAL! Date: {self.datas[0].datetime.date(0)}, Cash: {self.broker.get_cash()}, Price: {self.datas[0].close[0]}")


def run_backtest():
    cerebro = bt.Cerebro()

    # df = pd.read_csv('BTCUSDT_1d_2021_2025_cleaned.csv')
    # 去掉 fromdate / todate 做最小化测试
    data = bt.feeds.GenericCSVData(
        dataname='BTCUSDT_1d_2021_2025_cleaned.csv',
        dtformat='%Y-%m-%d',
        # dtformat='%Y/%m/%d',
        datetime=0,
        time=-1,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        skiprows=1,  # 跳过表头
        # fromdate=datetime.datetime(2021,1,1),
        # todate=datetime.datetime(2025,1,1),
    )

    cerebro.adddata(data)
    print('Data length:', len(data))

    cerebro.addstrategy(DoubleMAStrategy)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    results = cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()

if __name__ == '__main__':
    run_backtest()
