from marketdata import MarketData
from tradingsystem import TradingSystem
from strategy import Strategy


def evaluate(strategy, type, files):
    strategy.clear()
    data = MarketData()

    ts = TradingSystem()

    for instrument, file in files.items():
        ts.createBook(instrument)
        ts.subscribe(instrument, strategy)
        if type == MarketData.TICK:
            data.loadBBGTick(file, instrument)
        elif type == MarketData.HIST:
            data.loadYAHOOHist(file, instrument)
        elif type == MarketData.INTR:
            data.loadBBGIntr(file, instrument)

    data.run(ts)

    ts.submit(strategy.id, strategy.close())
    return strategy.summary()


def evaluateTick(strategy, files):
    return evaluate(strategy, MarketData.TICK, files)


def evaluateHist(strategy, files):
    return evaluate(strategy, MarketData.HIST, files)


def evaluateIntr(strategy, files):
    return evaluate(strategy, MarketData.INTR, files)
