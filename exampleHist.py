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

print(evaluateHist(BuynHold(), '^BVSP.csv'))
print(evaluateHist(MAVG(), '^BVSP.csv'))