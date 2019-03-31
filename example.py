from backtesting import Strategy, Order, Event, evaluate

class MyStrategy(Strategy):
  
  def __init__(self):
    self.bought = False

  def push(self, event):
    if event.type == Event.ASK and not self.bought:
      self.bought = True
      return Order(100, 0)      
    return None

print(evaluate(MyStrategy(), '2018-03-07.csv'))

# To Do: Separar portfolio e enviar o estado no evento push