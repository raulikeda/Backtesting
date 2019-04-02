from backtesting import Strategy, Order, Event, evaluate

class BuynHold(Strategy):
  
  def __init__(self):
    self.bought = False

  def push(self, event):
    if event.type == Event.ASK and not self.bought:
      self.bought = True
      return Order(100, 0)      
    return None

class MAVG(Strategy):
  
  def __init__(self):
    self.signal = 0
    self.prices = []
    self.size = 100 #moving average window

  def push(self, event):
    if event.type == Event.TRADE:
      self.prices.append(event.price)
      if len(self.prices) >= self.size:
        del self.prices[0]
        avg = sum(self.prices) / len(self.prices)
        order = None
        if avg < event.price*1.002:
          if self.signal == 0:
            order = Order(-100, 0)
          elif self.signal == 1:
            order = Order(-200, 0)
          self.signal = -1
        elif avg > event.price*0.998:
          if self.signal == 0:
            order = Order(100, 0)
          elif self.signal == -1:
            order = Order(200, 0)
          self.signal = 1
        return order
    return None

print(evaluate(BuynHold(), '2018-03-07.csv'))
print(evaluate(MAVG(), '2018-03-07.csv'))


# To Do: Separar portfolio e enviar o estado no evento push