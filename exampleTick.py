from backtesting import evaluateTick
from strategy import Strategy
from order import Order
from event import Event

import numpy as np

class BuynHoldTick(Strategy):
  
  def __init__(self):
    self.bought = False

  def push(self, event):
    # If didnt buy yet, do it
    if event.type == Event.TRADE:
      if not self.bought:
        self.bought = True
        # Send one buy order once
        return [Order(event.instrument, 100, 0)]
      return []
    return []

class MAVGTick(Strategy):
  
  def __init__(self):
    self.signal = 0
    self.prices = []
    self.size = 1000
    self.std = 0

  def push(self, event):
    if event.type == Event.TRADE:
      price = event.price
      self.prices.append(price)
      orders = []
      if len(self.prices) == self.size:
        std = np.array(self.prices).std()
        mavg = sum(self.prices)/self.size

        if price >= mavg + std:
          if self.signal == 1:
            orders.append(Order(event.instrument, -100, 0))
          if self.signal == 0:
            orders.append(Order(event.instrument, -100, 0))
          self.signal = -1
        elif price <= mavg - std:
          if self.signal == -1:
            orders.append(Order(event.instrument, 100, 0))
          if self.signal == 0:
            orders.append(Order(event.instrument, 100, 0))
          self.signal = 1        

        del self.prices[0]

      return orders
    return []

print(evaluateTick(BuynHoldTick(), {'PETR4':'2018-03-07.csv'}))
print(evaluateTick(MAVGTick(), {'PETR4':'2018-03-07.csv'}))