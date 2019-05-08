from event import Event
from datetime import datetime

class MarketData():

  TICK, HIST, INTR = ['TICK', 'HIST', 'INTR']

  def __init__(self):

    self.events = {}

  def loadBBGTick(self, file, instrument):

    with open(file,'r') as file:
      data = file.read()
    
    events = data.split('\n')
    events = events[1:]
    for event in events:
      cols = event.split(';')
      if len(cols) == 4:
        date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
        price = float(cols[2].replace(',','.'))
        quantity = int(cols[3])
        type = cols[1]

        if date.toordinal() not in self.events:
          self.events[date.toordinal()] = []

        self.events[date.toordinal()].append(Event(instrument, date, type, price, quantity))

  def loadYAHOOHist(self, file, instrument, type = Event.CANDLE):

    with open(file,'r') as file:
      data = file.read()

    events = data.split('\n')
    events = events[1:]
    for event in events:      
      cols = event.split(',')
      if len(cols) == 7 and cols[1] != 'null':

        date = datetime.strptime(cols[0], '%Y-%m-%d')
        price = (float(cols[1]), float(cols[2]), float(cols[3]), float(cols[5]))
        quantity = int(cols[6])
        
        if date.toordinal() not in self.events:
          self.events[date.toordinal()] = []
          
        self.events[date.toordinal()].append(Event(instrument, date, type, price, quantity))

  def loadBBGIntr(self, file, instrument, type = Event.CANDLE):

    with open(file,'r') as file:
      data = file.read()

    events = data.split('\n')
    events = events[1:]
    for event in events:      
      cols = event.split(';')
      if len(cols) == 5:

        date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
        price = (float(cols[1].replace(',','.')), 
                 float(cols[3].replace(',','.')), 
                 float(cols[4].replace(',','.')), 
                 float(cols[2].replace(',','.')))
        quantity = 0
        
        if date.timestamp() not in self.events:
          self.events[date.timestamp()] = []        
          
        self.events[date.timestamp()].append(Event(instrument, date, type, price, quantity))

  def run(self, ts):
    dates = list(self.events.keys())
    dates.sort()
    for date in dates:
      for event in self.events[date]:
        ts.inject(event)