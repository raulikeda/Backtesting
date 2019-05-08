class Order():

  id = 0

  NEW, PARTIAL, FILLED, REJECTED, CANCELED = ['NEW', 'PARTIAL', 'FILLED', 'REJECTED', 'CANCELED']

  @staticmethod
  def nextId():
    Order.id += 1
    return Order.id

  def __init__(self, instrument, quantity, price):
    self.id = Order.nextId()
    self.owner = 0
    self.instrument = instrument
    self.status = Order.NEW
    self.timestamp = ''
    self.quantity = quantity
    self.price = price
    self.executed = 0
    self.average = 0
  
  def print(self):
    return '{0} - {1} - {5}: {2}/{3}@{4}'.format(self.id, self.timestamp, self.executed, self.quantity, self.price, self.instrument)
