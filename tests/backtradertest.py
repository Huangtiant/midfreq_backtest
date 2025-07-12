import backtrader as bt

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    print("starting portfolio value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print("final portfolio value: %.2f" % cerebro.broker.getvalue()) 