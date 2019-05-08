def sign(number):
  if number > 0:
    return 1
  elif number < 0:
    return -1
  return 0

class Event():

  BID, ASK, TRADE, CANDLE = ['BID', 'ASK', 'TRADE', 'CANDLE']

  def __init__(self, instrument, timestamp, type, price, quantity):
    self.instrument = instrument
    self.timestamp = timestamp
    self.type = type
    self.price = price
    self.quantity = quantity