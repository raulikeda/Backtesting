from backtesting import evaluateTick
from strategy import Strategy
from order import Order
from event import Event

import numpy as np
import random


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

    def fill(self, instrument, price, quantity, status):
        super().fill(instrument, price, quantity, status)
        self.side += quantity
        print(self.position)


class CrazyGambler(Strategy):
    def __init__(self):
        self.i = 0
        self.pos = 0
        self.avg = 0

    def push(self, event):
        orders = []
        if event.type == Event.TRADE:
            self.i += 1
            if self.i == 500:
                orders.append(Order(event.instrument, 1, 0))
                self.pos = 1
                self.avg = event.price
                print("{0} {1}".format(self.pos, self.avg))
            if event.price <= self.avg - 0.05:
                orders.append(Order(event.instrument, self.pos, 0))
                self.pos += self.pos
                self.avg += event.price
                self.avg /= 2
                print("{0} {1}".format(self.pos, self.avg))
        return orders


class BuynHoldTick(Strategy):

    def __init__(self):
        self.bought = False

    def push(self, event):
        # If didnt buy yet, do it
        if event.type == Event.TRADE:
            if not self.bought:
                self.bought = True
                # Send one buy order once
                return [Order(event.instrument, 100, 0)]
            return []
        return []


class MAVGTick(Strategy):

    def __init__(self):
        self.signal = 0
        self.prices = []
        self.size = 1000
        self.std = 0

    def push(self, event):
        if event.type == Event.TRADE:
            price = event.price
            self.prices.append(price)
            orders = []
            if len(self.prices) == self.size:
                std = np.array(self.prices).std()
                mavg = sum(self.prices)/self.size

                if price >= mavg + std:
                    if self.signal == 1:
                        orders.append(Order(event.instrument, -100, 0))
                        orders.append(Order(event.instrument, -100, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, -100, 0))
                    self.signal = -1
                elif price <= mavg - std:
                    if self.signal == -1:
                        orders.append(Order(event.instrument, 200, 0))
                    if self.signal == 0:
                        orders.append(Order(event.instrument, 100, 0))
                    self.signal = 1

                del self.prices[0]

            return orders
        return []


#print(evaluateTick(BuynHoldTick(), {'PETR4': '2018-03-07.csv'}))
#print(evaluateTick(MAVGTick(), {'PETR4': '2018-03-07.csv'}))
#print(evaluateTick(CrazyGambler(), {'PETR4': '2018-03-07.csv'}))
print(evaluateTick(MonkeyTrade(), {'PETR4': '2018-03-07.csv'}))
