from backtesting import Strategy, Order, Event, evaluateHist
import numpy as np

class RSI(Strategy):

  OVERBOUGHT = 65
  OVERSOLD = 40
  SIZE = 60

  def __init__(self):
    self.prices = []
    self.last_price = 0
    self.rs = []
    self.signal = 0

  def _get_rs(self):
    slice_prices = self.prices
    if len(self.prices) > self.SIZE:
      slice_prices = self.prices[-self.SIZE:]
    highs = []
    lows = []
    for i in range(1, len(slice_prices)):
      ret = slice_prices[i]
      if slice_prices[i] > slice_prices[i - 1]:
        highs.append(ret)
      else:
        lows.append(ret)
    avg_high = sum(highs) / len(slice_prices) if len(slice_prices) else 0
    avg_low = sum(lows) / len(slice_prices) if len(slice_prices) else 1
    return avg_high / avg_low if avg_low else 0

  def _calculate_rsi(self):
    rs = self._get_rs()
    rsi = 100 - 100 /(1 + rs)
    return rsi

  def push(self, event):
    orders = []
    price = event.price[3]
    self.prices.append(price)
    if len(self.prices) > 0:
      rsi = self._calculate_rsi()
      if rsi >= self.OVERBOUGHT:
        if self.signal == 1:
          orders.append(Order(-1, 0))
          orders.append(Order(-1, 0))
        if self.signal == 0:
          orders.append(Order(-1, 0))
        self.signal = -1
      elif rsi <= self.OVERSOLD:
        if self.signal == -1:
          orders.append(Order(1, 0))
          orders.append(Order(1, 0))
        if self.signal == 0:
          orders.append(Order(1, 0))
        self.signal = 1
    return orders

print(evaluateHist(RSI(), '^BVSP.csv'))