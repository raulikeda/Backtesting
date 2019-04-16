import math

class Event():

  BID, ASK, TRADE, CANDLE = ['BID', 'ASK', 'TRADE', 'CANDLE']

  def __init__(self, timestamp, type, price, quantity):
    self.timestamp = timestamp
    self.type = type
    self.price = price
    self.quantity = quantity

class Leg():

  def __init__(self):
    self.sign = 0
    self.price = [0, 0, 0]
    self.quantity = [0, 0, 0]

  def print(self):
    if self.sign == 1:
      return 'B:{0}@{1} S:{2}@{3}'.format(self.price[1], self.quantity[1], self.price[-1], self.quantity[-1])
    elif self.sign == -1:
      return 'S:{2}@{3} B:{0}@{1}'.format(self.price[1], self.quantity[1], self.price[-1], self.quantity[-1])
    else:
      return ''


class Order():

  id = 1

  def __init__(self, quantity, price):
    self.id = Order.id
    Order.id += 1
    self.timestamp = ''
    self.quantity = quantity
    self.price = price
    self.executed = 0
  
  def print(self):
    return '{0} - {1}: {2}/{3}@{4}'.format(self.id, self.timestamp, self.executed, self.quantity, self.price)

class Book():

  def __init__(self):

    #portfolio
    self.samplesize = 0
    self.position = 0
    self.result = 0
    self.notional = 0
    self.trades = 0
    self.orders = []
    self.legs = [Leg()] #sign, buy price, buy quantity, sell quantity, sell price

    #market data
    self.pos = 0
    self.events = []
    self.bid = None
    self.ask = None
    self.trade = None

    self.timestamp = None  

  @staticmethod
  def sign(number):
    if number > 0:
      return 1
    elif number < 0:
      return -1
    return 0

  def loadTick(self, file):
    with open(file,'r') as file:
      data = file.read()
    
    events = data.split('\n')
    events = events[1:]
    for event in events:
      cols = event.split(';')
      if len(cols) == 4:
        price = float(cols[2].replace(',','.'))
        quantity = int(cols[3])
        self.events.append(Event(cols[0], cols[1], price, quantity))

  def loadHist(self, file):
    with open(file,'r') as file:
      data = file.read()

    events = data.split('\n')
    events = events[1:]
    for event in events:      
      cols = event.split(',')
      if len(cols) == 7 and cols[1] != 'null':        
        price = (float(cols[1]), float(cols[2]), float(cols[3]), float(cols[4]))
        quantity = int(cols[6])
        self.events.append(Event(cols[0], Event.CANDLE, price, quantity))

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
        self.samplesize += 1
        self.trade = event
      elif event.type == Event.CANDLE:
        self.samplesize += 1
        self.bid = Event(event.timestamp, Event.BID, event.price[3], event.quantity)
        self.ask = Event(event.timestamp, Event.ASK, event.price[3], event.quantity)
        self.trade = event
      return event
    return None
  
  def order(self, order):
    if order is not None:
      if Book.sign(self.position) * Book.sign(self.position + order.quantity) == -1:
        raise ValueError('Error closing position: more quantity than necessary.')

      if order.quantity > 0 and self.ask is not None:
        price = self.ask.price
        quantity = order.quantity #self.ask.quantity
      elif order.quantity < 0 and self.bid is not None:
        price = self.bid.price
        quantity = order.quantity #self.bid.quantity
      else:
        price = 0

      if price != 0:

        self.trades += 1
        self.position += quantity
        self.result -= quantity*price
        if quantity > 0:
          self.notional += quantity*price
        else:
          self.notional -= quantity*price

        if quantity != 0:
          idx = Book.sign(quantity)
          self.legs[-1].price[idx] = (self.legs[-1].price[idx]*self.legs[-1].quantity[idx] + price*quantity)/(self.legs[-1].quantity[idx] + quantity)
          self.legs[-1].quantity[idx] += quantity

        if Book.sign(self.position) == 0:
          self.legs.append(Leg())
        elif self.legs[-1].sign == 0:
          self.legs[-1].sign = Book.sign(self.position)

        order.executed = quantity
        order.price = price      
        self.orders.append(order)

  def close(self):
    if self.position != 0:
      self.order(Order(-self.position, 0))

  def summary(self, orders=False, tax=0.00024, fee=0):
    
    nt = 0
    hr = 0
    pnl = 0
    ret = 0
    net = 0
    mp = -float("inf")
    md = float("inf")
    for leg in self.legs:
      if leg.sign != 0:
        nt += 1
        pro = -(leg.price[-1]*leg.quantity[-1] + leg.price[1]*leg.quantity[1])
        pnl += pro
        net += -leg.price[-1]*leg.quantity[-1] + leg.price[1]*leg.quantity[1]
        ret += pro / leg.price[leg.sign]
        if pro > 0:
          hr += 1
        if pro > mp:
          mp = pro
        if pro < md:
          md = pro

    res = 'Number of events: {0}\n'.format(self.samplesize)
    res += 'Number of trades: {0}\n'.format(nt)
    res += 'Gross P&L: {0:.2f}\n'.format(pnl)
    res += 'Gross Accumulated return: {0:.2f}%\n'.format(100 * ret)

    net = pnl - net * tax - nt * fee
    res += 'Net P&L: {0:.2f}\n'.format(net)

    res += 'Hitting ratio: {0:.2f}%\n'.format(100*hr/nt)
    res += 'Max Profit: {0:.2f}\n'.format(mp)
    res += 'Max Drawdown: {0:.2f}\n'.format(md)

    res += '\nTrades:\n'
    for leg in self.legs:
      res += leg.print() + '\n'

    if orders:
      res += '\nOrders:\n'
      for order in self.orders:
        res += order.print()+'\n'

    return res

  def evaluate(self, strategy):
    event = self.pop()
    while event is not None:
      orders = strategy.push(event)    
      for order in orders:
        self.order(order)
      event = self.pop()
  
    self.close()

class Strategy():

  def __init__(self):
    pass

  def push(self, event):
    pass

def evaluateTick(strategy, file):
  book = Book()
  book.loadTick(file)
  book.evaluate(strategy)
  return book.summary(False)

def evaluateHist(strategy, file):
  book = Book()
  book.loadHist(file)
  book.evaluate(strategy)
  return book.summary(False)