from backtesting import evaluateHist
from strategy import Strategy
from order import Order
import numpy as np


class BuynHold(Strategy):

    def __init__(self):
        self.bought = False

    def push(self, event):
        # If didnt buy yet, do it
        if not self.bought:
            self.bought = True
            # Send one buy order once
            return [Order(event.instrument, 1, 0)]

        # If you need partial result in case of feedback training
        # result = self.partialResult()

        return []


class MAVG(Strategy):

    def __init__(self):
        self.signal = 0
        self.prices = []
        self.sizeq = 17
        self.sizes = 72
        self.std = 0
        self.ref = 0

    def push(self, event):
        price = event.price[3]
        self.prices.append(price)
        orders = []

        if len(self.prices) >= self.sizeq:
            maq = sum(self.prices[-self.sizeq:])/self.sizeq
        if len(self.prices) == self.sizes:
            mas = sum(self.prices)/self.sizes

            if maq > mas and self.signal != 1:
                if self.signal == -1:
                    orders.append(Order(event.instrument, 1, 0))
                orders.append(Order(event.instrument, 1, 0))
                self.signal = 1
            elif maq < mas and self.signal != -1:
                if self.signal == 1:
                    orders.append(Order(event.instrument, -1, 0))
                orders.append(Order(event.instrument, -1, 0))
                self.signal = -1

            del self.prices[0]

        return orders


# By @marcelogdeandrade
class RSI(Strategy):

    OVERBOUGHT = 65
    OVERSOLD = 40
    SIZE = 5

    def __init__(self):
        self.prices = []
        self.last_price = 0
        self.rs = []
        self.signal = 0

    def _get_rs(self):
        slice_prices = self.prices
        if len(self.prices) > self.SIZE:
            slice_prices = self.prices[-self.SIZE:]
        highs = []
        lows = []
        for i in range(1, len(slice_prices)):
            ret = slice_prices[i]
            if slice_prices[i] > slice_prices[i - 1]:
                highs.append(ret)
            else:
                lows.append(ret)
        avg_high = sum(highs) / len(slice_prices) if len(slice_prices) else 0
        avg_low = sum(lows) / len(slice_prices) if len(slice_prices) else 1
        return avg_high / avg_low if avg_low else 0

    def _calculate_rsi(self):
        rs = self._get_rs()
        rsi = 100 - 100 / (1 + rs)
        return rsi

    def push(self, event):
        orders = []
        price = event.price[3]
        self.prices.append(price)
        if len(self.prices) > 0:
            rsi = self._calculate_rsi()
            if rsi >= self.OVERBOUGHT:
                if self.signal == 1:
                    orders.append(Order(event.instrument, -1, 0))
                    orders.append(Order(event.instrument, -1, 0))
                if self.signal == 0:
                    orders.append(Order(event.instrument, -1, 0))
                self.signal = -1
            elif rsi <= self.OVERSOLD:
                if self.signal == -1:
                    orders.append(Order(event.instrument, 1, 0))
                    orders.append(Order(event.instrument, 1, 0))
                if self.signal == 0:
                    orders.append(Order(event.instrument, 1, 0))
                self.signal = 1
        return orders

# By @pedrocunial


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
                        orders += [Order(event.instrument, -1, 0),
                                   Order(event.instrument, -1, 0)]
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
                        orders += [Order(event.instrument, 1, 0),
                                   Order(event.instrument, 1, 0)]
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


print(evaluateHist(BuynHold(), {'IBOV': '^BVSP.csv'}))
print(evaluateHist(MAVG(), {'IBOV': '^BVSP.csv'}))
print(evaluateHist(RSI(), {'IBOV': '^BVSP.csv'}))
print(evaluateHist(SAR(), {'IBOV': '^BVSP.csv'}))
