class Event():

  BID, ASK, TRADE = ['BID', 'ASK', 'TRADE']

  def __init__(self, timestamp, type, price, quantity):
    self.timestamp = timestamp
    self.type = type
    self.price = price
    self.quantity = quantity

class Order():

  id = 1

  def __init__(self, timestamp, quantity, price):
    self.id = Order.id
    Order.id += 1
    self.timestamp = timestamp
    self.quantity = quantity
    self.price = price
    self.executed = 0
  
  def print(self):
    return '{0} - {1}: {2}/{3}@{4}'.format(self.id, self.timestamp, self.executed, self.quantity, self.price)

class Book():

  def __init__(self):

    #portfolio
    self.position = 0
    self.result = 0
    self.trades = 0
    self.orders = []

    #market data
    self.pos = 0
    self.events = []
    self.bid = None
    self.ask = None
    self.trade = None

    self.timestamp = None

  def load(self, file):
    with open(file,'r') as file:
      data = file.read()
    
    events = data.split('\n')
    for event in events:
      cols = event.split(',')
      self.events.append(Event(cols[0], cols[1], cols[2], cols[3]))

  def pop(self):
    if self.pos < len(self.events):
      event = self.events[self.pos]
      self.timestamp = event.timestamp
      self.pos += 1
      if event.type == Event.BID:
        self.bid = event
      elif event.type == Event.ASK:
        self.ask = event
      elif event.type == Event.TRADE:
        self.trade = event
      return event
    return None
  
  def order(self, order):
    if order is not None:
      
      if order.quantity > 0 and self.ask is not None:
        price = self.ask.price
        quantity = self.ask.quantity
      elif order.quantity < 0 and self.bid is not None:
        price = self.bid.price
        quantity = self.bid.quantity
      else:
        price = 0

      if price != 0:
        self.trades += 1
        self.position += quantity
        self.result -= quantity*price

      order.executed = quantity
      order.price = price
      self.orders.append(order)

  def close(self):
    if self.position != 0:
      self.order(Order(self.timestamp, -self.position, 0))

  def summary(self, orders=False):
    res = 'Number of trades: {0}\n'.format(self.trades)
    res += 'P&L: {0:.2f}\n'.format(self.result)
    if orders:
      for order in self.orders:
        res += order.print()
    return res

class Strategy():

  def __init__(self):
    pass

  def push(self, event):
    pass

def evaluate(strategy, file):
  book = Book()
  book.load(file)

  event = book.pop()
  while event is not None:
    order = strategy.push(event)
    if order is not None:
      book.order(order)
  
  book.close()
  return book.summary()