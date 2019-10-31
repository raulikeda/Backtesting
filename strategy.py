import math
from event import Event, sign
from order import Order


class Strategy():

    id = 0

    @staticmethod
    def nextId():
        Strategy.id += 1
        return Strategy.id

    def __init__(self):
        pass

    def clear(self):
        self.id = Strategy.nextId()

        self.position = {}
        self.last = {}

        self.legs = []

        self.result = {}
        self.notional = {}

        self.orders = []

    def cancel(self, owner, id):
        pass

    def submit(self, id, orders):
        pass

    def event(self, event):

        self.last[event.instrument] = event.price
        return self.push(event)

    def push(self, event):
        pass

    def fill(self, id, instrument, price, quantity, status):

        if price != 0:

            if instrument not in self.position:
                self.position[instrument] = 0

            if instrument not in self.result:
                self.result[instrument] = 0

            if instrument not in self.notional:
                self.notional[instrument] = 0

            self.position[instrument] += quantity
            self.result[instrument] -= quantity*price

            if quantity > 0:
                self.notional[instrument] += quantity*price
            else:
                self.notional[instrument] -= quantity*price

            if self.zeroed():
                self.legs.append((self.totalResult(), self.totalNotional()))

    def zeroed(self):
        for position in self.position.values():
            if position != 0:
                return False
        return True

    def close(self):

        orders = []
        for instrument, position in self.position.items():
            if position != 0:
                orders.append(Order(instrument, -position, 0))

        return orders

    def partialResult(self):
        res = {}
        for instrument, result in self.result.items():
            res[instrument] = result + \
                self.position[instrument]*self.last[instrument]
        return res

    def totalNotional(self):
        res = 0
        for notional in self.notional.values():
            res += notional
        return res

    def totalResult(self):
        res = 0
        for result in self.result.values():
            res += result
        return res

    def summary(self, tax=0.00024, fee=0):

        # Number of trades
        nt = len(self.legs)

        # Hitting ratio
        hr = 0

        # P&L
        pnl = 0

        # Accumulated Return
        ret = 0

        net = 0
        avg = 0
        mp = -float("inf")
        md = float("inf")
        amo = 0
        if nt > 0:
            pnl = self.legs[-1][0]

            amo = self.legs[-1][1]
            ret = pnl / (amo/2)

            if pnl > 0:
                hr += 1

            mp = self.legs[0][0]
            md = self.legs[0][0]

            avg = self.legs[0][0]/(self.legs[0][1]/2)

            i = 1
            while i < len(self.legs):
                res = self.legs[i][0]-self.legs[i-1][0]
                amo = (self.legs[i][1]-self.legs[i-1][1])/2
                avg += res/amo

                if res > mp:
                    mp = res
                if res < md:
                    md = res

                if res > 0:
                    hr += 1

                i += 1

            avg = avg/nt
            hr = hr/nt

        res = ''
        res += 'Number of trades: {0}\n'.format(nt)
        res += 'Gross P&L: {0:.2f}\n'.format(pnl)
        res += 'Gross Accumulated return: {0:.2f}%\n'.format(100 * ret)
        res += 'Gross Average Return: {0:.2f}%\n'.format(100 * avg)

        net = pnl - amo * tax - nt * fee
        res += 'Net P&L: {0:.2f}\n'.format(net)

        res += 'Hitting ratio: {0:.2f}%\n'.format(100*hr)
        res += 'Max Profit: {0:.2f}\n'.format(mp)
        res += 'Max Drawdown: {0:.2f}\n'.format(md)

        return res
