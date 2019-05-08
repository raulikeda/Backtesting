from event import Event
from order import Order
import math

class Book():

  def __init__(self, instrument, fill):

    self.instrument = instrument
    self.fill = fill

    #market data
    self.bid = None
    self.ask = None
    self.trade = None
    self.timestamp = None  

    self.orders = []

  def inject(self, event):
    if event.instrument == self.instrument:
      self.timestamp = event.timestamp

      if event.type == Event.CANDLE:
        event.price = event.price[3]
      
      if event.type == Event.BID or event.type == Event.CANDLE:
        self.bid = event
        for order in self.orders:
          if order.quantity < 0:
            if order.price <= event.price:
              rem = order.quantity - order.executed
              
              if event.quantity == 0:
                qty = rem
              else:
                qty = max(rem, -event.quantity)

              average = order.average * order.executed + qty * event.price

              order.executed += qty
              order.average = average / order.executed

              if order.quantity == order.executed:
                order.status = Order.FILLED
              
              self.fill(order.id, event.price, qty, order.status)
          
      if event.type == Event.ASK or event.type == Event.CANDLE:
        self.ask = event
        for order in self.orders:
          if order.quantity > 0:
            if order.price >= event.price:
              rem = order.quantity - order.executed

              if event.quantity == 0:
                qty = rem
              else:
                qty = min(rem, event.quantity)

              average = order.average * order.executed + qty * event.price

              order.executed += qty
              order.average = average / order.executed

              if order.quantity == order.executed:
                order.status = Order.FILLED
              
              self.fill(order.id, event.price, qty, order.status)

      if event.type == Event.TRADE:
        self.trade = event
        for order in self.orders:
          if order.quantity > 0 and order.price >= event.price:
            rem = order.quantity - order.executed

            if event.quantity == 0:
              qty = rem
            else:
              qty = min(rem, event.quantity)

            average = order.average * order.executed + qty * event.price

            order.executed += qty
            order.average = average / order.executed

            if order.quantity == order.executed:
              order.status = Order.FILLED
            
            self.fill(order.id, event.price, qty, order.status)

          if order.quantity < 0 and order.price <= event.price:
            rem = order.quantity - order.executed

            if event.quantity == 0:
              qty = rem
            else:
              qty = max(rem, -event.quantity)

            average = order.average * order.executed + qty * event.price

            order.executed += qty
            order.average = average / order.executed

            if order.quantity == order.executed:
              order.status = Order.FILLED
            
            self.fill(order.id, event.price, qty, order.status)
      
      i = 0
      while i < len(self.orders):
        if self.orders[i].status == Order.FILLED:
          del self.orders[i]
        else:
          i += 1

  def submit(self, order):
    if order is not None:
      if order.price == 0: #MKT
        if order.quantity > 0:
          if self.ask.quantity == 0:
            order.executed = order.quantity
          else:
            order.executed = min([self.ask.quantity, order.quantity])

          order.average = self.ask.price
          order.status = Order.FILLED

          self.fill(order.id, order.average, order.executed, order.status)

        elif order.quantity < 0:
          if self.bid.quantity == 0:
            order.executed = order.quantity
          else:
            order.executed = max([-self.bid.quantity, order.quantity])

          order.average = self.bid.price
          order.status = Order.FILLED

          self.fill(order.id, order.average, order.executed, order.status)

      else: #LMT order
        if order.quantity > 0 and order.price >= self.ask.price:
          if self.ask.quantity == 0:
            order.executed = order.quantity
            order.average = self.ask.price
            order.status = Order.FILLED
          else:
            order.executed = min([self.ask.quantity, order.quantity])
            order.average = self.ask.price
            if order.executed == order.quantity:
              order.status = Order.FILLED
            else:
              order.status = Order.PARTIAL
              self.orders.append(order)
          self.fill(order.id, order.average, order.executed, order.status)
        elif order.quantity < 0 and order.price <= self.bid.price:
          if self.bid.quantity == 0:
            order.executed = order.quantity
            order.average = self.bid.price
            order.status = Order.FILLED
          else:
            order.executed = max([-self.bid.quantity, order.quantity])
            order.average = self.bid.price
            if order.executed == order.quantity:
              order.status = Order.FILLED
            else:
              order.status = Order.PARTIAL
              self.orders.append(order)
          self.fill(order.id, order.average, order.executed, order.status)
        elif order.quantity != 0:
          self.orders.append(order)

  def cancel(self, id):
    i = 0
    while i < len(self.orders):
      if self.orders[i].id == id:
        order = self.orders[i]
        del self.orders[i]
        order.status = Order.CANCELED        
        self.fill(order.id, 0, 0, order.status)
        i = len(self.orders)
      else:
        i += 1