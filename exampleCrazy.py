from backtesting import evaluateHist
from strategy import Strategy
from order import Order
from event import Event

import numpy as np
import random


class Martingale(Strategy):

    def __init__(self):
        self.trades = []
        self.size = 0
        self.average = 0

    def push(self, event):

        price = event.price[3]

        orders = []

        if self.size == 0:
            orders.append(Order(event.instrument, 1, 0))
            self.size = 1
            self.average = price
            print("{0} {1} {2}".format(
                price, self.average, self.size))

        elif (price/self.average - 1) <= -0.01:
            orders.append(Order(event.instrument, self.size, 0))
            self.size *= 2
            self.average += price
            self.average /= 2
            print("{0} {1} {2}".format(
                price, self.average, self.size))

        return orders

#print(evaluateHist(Martingale(), {'IBOV':'^BVSP.csv'}))

class MonkeyTrade(Strategy):
    def __init__(self):
        self.side = 0
        self.gain = 0
        self.price = 0

    def push(self, event):
        orders = []

        if random.randint(1, 10) == 1:
            side = random.choice([-1, 1])
            if side != self.side:
                orders.append(Order(event.instrument, -self.side, 0))
                orders.append(Order(event.instrument, side, 0))
                self.side = side

        return orders

print(evaluateHist(MonkeyTrade(), {'IBOV':'^BVSP.csv'}))
