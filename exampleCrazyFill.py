from backtesting import evaluateHist, evaluateTick
from strategy import Strategy
from order import Order
from event import Event

import numpy as np
import random


class MartingaleG(Strategy):

    def __init__(self):
        self.trades = []
        self.size = 0
        self.average = 0
        self.enabled = True

    def push(self, event):

        # price = event.price[3]
        price = event.price

        orders = []

        if self.enabled:

            if self.size == 0:
                if event.type == event.ASK:
                    orders.append(Order(event.instrument, 1, 0))
                    self.size = 1
                    self.average = price
                    print("{0} {1} {2}".format(
                        price, self.average, self.size))

            elif (price/self.average - 1) <= -0.002:
                orders.append(Order(event.instrument, self.size, 0))
                self.size *= 2
                self.average += price
                self.average /= 2
                print("{0} {1} {2}".format(
                    price, self.average, self.size))

            # Stop Gain: Close position if gain >= 1% and go home
            elif (price/self.average - 1) >= 0.01:
                # if size == 1, close position
                orders.append(Order(event.instrument, -self.size, 0))
                self.size = 0
                self.average = price
                print("{0} {1} {2}".format(
                    price, self.average, self.size))

                self.enabled = False

        return orders


# print(evaluateHist(MartingaleG(), {'IBOV': '^BVSP.csv'}))
#print(evaluateTick(MartingaleG(), {'PETR4': '2018-03-07.csv'}))


class MonkeyTradeGL(Strategy):
    def __init__(self):
        self.side = 0
        self.gain = 0
        self.price = 0

    def push(self, event):
        orders = []
        price = event.price[3]
        #price = event.price

        if random.randint(1, 10) == 1:
            side = random.choice([-1, 1])
            if side != self.side:

                # Close position
                orders.append(Order(event.instrument, -self.side, 0))
                # Mount new position
                orders.append(Order(event.instrument, side, 0))

                self.price = price

                gain = Order(event.instrument, -side,
                             self.price + side * 0.05)

                # Save order id
                self.gain = gain.id
                # Send Stop Gain order
                orders.append(gain)

        # Stop Loss
        if self.side == 1 and price <= self.price * 0.95:
            # Send order to close position
            orders.append(Order(event.instrument, -self.side, 0))
            # Cancel Stop Gain order
            self.cancel(self.id, self.gain)
        elif self.side == -1 and price >= self.price * 0.05:
            # Send order to close position
            orders.append(Order(event.instrument, -self.side, 0))
            # Cancel Stop Gain order
            self.cancel(self.id, self.gain)

        if len(orders) > 0:
            for order in orders:
                if order.quantity != 0:
                    print(order.print())

        return orders

    # How to capture an order fill
    def fill(self, id, instrument, price, quantity, status):
        # Mandatory
        super().fill(id, instrument, price, quantity, status)

        # Need to identify if the id is the order id of interest
        if self.gain == id:
            print('$$')

        # Adjusting by quantity filled
        self.side += quantity

        # Position exists from Strategy class, you can use it
        print(self.position)


#
print(evaluateHist(MonkeyTradeGL(), {'IBOV': '^BVSP.csv'}))
# print(evaluateTick(MonkeyTradeGL(), {'PETR4': '2018-03-07.csv'}))
