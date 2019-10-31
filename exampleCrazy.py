from backtesting import evaluateTick
from strategy import Strategy
from order import Order
from event import Event

import numpy as np
import random


class CrazyTick(Strategy):
    def __init__(self):
        self.trades = []
        self.size = 0
        self.average = 0
        self.i = 0

    def push(self, event):
        orders = []
        if event.type == Event.TRADE:

            self.i += 1
            if self.i >= 500:
                if self.size == 0:
                    orders.append(Order(event.instrument, 1, 0))
                    self.size = 1
                    self.average = event.price
                    print("{0} {1} {2}".format(
                        event.price, self.average, self.size))

                if event.price - self.average <= -0.05:
                    orders.append(Order(event.instrument, self.size, 0))
                    self.size *= 2
                    self.average += event.price
                    self.average /= 2
                    print("{0} {1} {2}".format(
                        event.price, self.average, self.size))

        return orders


#print(evaluateTick(CrazyTick(), {'PETR4': '2018-03-07.csv'}))

class MonkeyTrade(Strategy):
    def __init__(self):
        self.side = 0
        self.gain = 0
        self.price = 0

    def push(self, event):
        orders = []
        if random.randint(1, 5000) == 1:
            side = random.choice([-1, 1])
            if side != self.side:
                orders.append(Order(event.instrument, -self.side, 0))
                orders.append(Order(event.instrument, side, 0))

                self.price = event.price

                gain = Order(event.instrument, -side,
                             event.price + side * 0.10)

                self.gain = gain.id
                orders.append(gain)

        if self.side == 1 and event.price <= self.price - 0.05:
            orders.append(Order(event.instrument, -self.side, 0))
            self.cancel(self.id, self.gain)
        elif self.side == -1 and event.price >= self.price + 0.05:
            orders.append(Order(event.instrument, -self.side, 0))
            self.cancel(self.id, self.gain)

        if len(orders) > 0:
            for order in orders:
                print(order.print())

        return orders

    def fill(self, id, instrument, price, quantity, status):
        super().fill(id, instrument, price, quantity, status)
        if self.gain == id:
            print('$$')
        self.side += quantity
        print(self.position)


print(evaluateTick(MonkeyTrade(), {'PETR4': '2018-03-07.csv'}))
