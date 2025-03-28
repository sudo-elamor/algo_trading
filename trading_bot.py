import yfinance as yf
import backtrader as bt
import datetime

# Define Trading Strategy
class MovingAverageStrategy(bt.Strategy):
    params = dict(short_period=10, long_period=50)

    def __init__(self):
        self.sma_short = bt.indicators.SMA(period=self.params.short_period)
        self.sma_long = bt.indicators.SMA(period=self.params.long_period)

    def next(self):
        if self.sma_short[0] > self.sma_long[0] and not self.position:
            self.buy()
        elif self.sma_short[0] < self.sma_long[0] and self.position:
            self.sell()

# Backtest Setup
cerebro = bt.Cerebro()
cerebro.addstrategy(MovingAverageStrategy)


# Fetch data using yfinance
fromdate = datetime.datetime(2023, 1, 1)
todate = datetime.datetime(2024, 1, 1)
df = yf.download("AAPL", start=fromdate.strftime("%Y-%m-%d"), end=todate.strftime("%Y-%m-%d"))

# Convert to Backtrader feed
data = bt.feeds.PandasData(dataname=df)

# Add Data to Backtrader
cerebro.adddata(data)
cerebro.broker.set_cash(10000)
cerebro.run()
cerebro.plot()
