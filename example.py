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
    self.size = 500 #moving average window
    self.alpha = 0.0003
    self.previous = None

  def push(self, event):
    if event.type == Event.TRADE:
      self.prices.append(event.price)
      if len(self.prices) >= self.size:
        avg = sum(self.prices) / len(self.prices)

        order = None

        if self.previous is not None:
          delta = avg - self.previous
        
          if delta <= -self.alpha:
            if self.signal == 0:
              order = Order(-100, 0)
            elif self.signal == 1:
              order = Order(-200, 0)
            self.signal = -1
          elif delta >= self.alpha:
            if self.signal == 0:
              order = Order(100, 0)
            elif self.signal == -1:
              order = Order(200, 0)
            self.signal = 1
          elif self.signal != 0:
            order = Order(-self.signal*100, 0)
            self.signal = 0

        self.previous = avg
        del self.prices[0]
        if order is not None:
          order.timestamp = event.timestamp                
        return order
    return None

print(evaluate(BuynHold(), '2018-03-07.csv'))
print(evaluate(MAVG(), '2018-03-07.csv'))


# To Do: Separar portfolio e enviar o estado no evento push