from backtesting import Strategy, Order, Event, evaluateHist
import numpy as np

class BuynHold(Strategy):
  
  def __init__(self):
    self.bought = False

  def push(self, event):
    # If didnt buy yet, do it
    if not self.bought:
      self.bought = True
      # Send one buy order once
      return [Order(1, 0)]
    return []

class MAVG(Strategy):
  
  def __init__(self):
    self.signal = 0
    self.prices = []
    self.size = 63    
    self.std = 0

  def push(self, event):
    price = event.price[3]
    self.prices.append(price)
    orders = []  
    if len(self.prices) == self.size:
      std = np.array(self.prices).std()
      mavg = sum(self.prices)/self.size

      if price >= mavg + std:
        if self.signal == 1:
          orders.append(Order(-1, 0))
          orders.append(Order(-1, 0))
        if self.signal == 0:
          orders.append(Order(-1, 0))
        self.signal = -1
      elif price <= mavg - std:
        if self.signal == -1:
          orders.append(Order(1, 0))
          orders.append(Order(1, 0))
        if self.signal == 0:
          orders.append(Order(1, 0))
        self.signal = 1

      del self.prices[0]

    return orders

class RSI(Strategy):

  OVERBOUGHT = 65
  OVERSOLD = 40

  def __init__(self):
    self.size = 60
    self.prices = []
    self.last_price = 0
    self.rs = []
    self.signal = 0

  def _get_rs(self):
    slice_prices = self.prices
    if len(self.prices) > self.size:
      slice_prices = self.prices[-self.size:]
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

  def push(self, event):
    orders = []
    price = event.price[3]
    self.prices.append(price)
    if len(self.prices) > 0:
      rs = self._get_rs()
      rsi = 100 - 100/(1 + rs)
      if rsi >= self.OVERBOUGHT:
        orders.append(Order(-1, 0))
        if self.signal == 1:
          orders.append(Order(-1, 0))
        self.signal = -1
      elif rsi <= self.OVERSOLD:
        orders.append(Order(1, 0))
        if self.signal == -1:
          orders.append(Order(1, 0))
        self.signal = 1
    return orders


print(evaluateHist(BuynHold(), '^BVSP.csv'))
print(evaluateHist(MAVG(), '^BVSP.csv'))
print(evaluateHist(RSI(), '^BVSP.csv'))