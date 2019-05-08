from backtesting import evaluateHist
from strategy import Strategy
from order import Order
from event import Event

class SAR(Strategy):

    def __init__(self):
        self.sar = []
        self.highs = []
        self.lows = []
        self.accel_min = 0.01
        self.accel_max = 0.1
        self.accel = self.accel_min
        self.crescent = True
        self.buying = 0

    def push(self, event):
        high = event.price[1]
        low = event.price[2]
        price = event.price[3]
        orders = []
        if self.sar:
            price = event.price[3]
            sar_prev = self.sar[-1]
            if self.crescent:
                sar_predict = sar_prev + self.accel * (self.highs[-1] -
                                                       sar_prev)
                if sar_predict > price:
                    self.crescent = False
                    if self.buying == 1:
                        orders += [Order(event.instrument, -1, 0), Order(event.instrument, -1, 0)]
                        self.buying = -1
                    elif self.buying == 0:
                        orders.append(Order(event.instrument, -1, 0))
                        self.buying = -1
                    self.accel = self.accel_min
                else:
                    self.accel = min(self.accel * 2, self.accel_max)
            else:
                sar_predict = sar_prev + self.accel * (self.lows[-1] -
                                                       sar_prev)
                if sar_predict < price:
                    self.crescent = True
                    if self.buying == -1:
                        orders += [Order(event.instrument, 1, 0), Order(event.instrument, 1, 0)]
                        self.buying = 1
                    elif self.buying == 0:
                        orders.append(Order(event.instrument, 1, 0))
                        self.buying = 1
                    self.accel = self.accel_min
                else:
                    self.accel = min(self.accel * 2, self.accel_max)
        else:
            sar_predict = price
        self.highs.append(high)
        self.lows.append(low)
        self.sar.append(sar_predict)
        return orders


print(evaluateHist(SAR(), {'IBOV':'^BVSP.csv'}))
