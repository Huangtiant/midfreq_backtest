import backtrader as bt
import pandas as pd
from utils.bom import recognize_BOM

class BOMStrategy(bt.Strategy):

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.active = False  # 未识别BOM形态前不开启交易逻辑
        self.df_buffer = []  # 用于缓存历史数据进行识别

    def next(self):
        # 构造 dataframe 缓存最近几根K线
        bar = {
            'datetime': self.datas[0].datetime.datetime(0),
            'open': self.datas[0].open[0],
            'high': self.datas[0].high[0],
            'low': self.datas[0].low[0],
            'close': self.datas[0].close[0],
        }
        self.df_buffer.append(bar)
        if len(self.df_buffer) < 10:
            return  # 数据太少，先跳过

        df = pd.DataFrame(self.df_buffer)

        # 如果尚未识别形态，则尝试识别
        if not self.active:
            if recognize_BOM(df):
                print(f"BOM recognized at {bar['datetime']}")
                self.active = True
            else:
                return  # 未识别，不做任何交易
        else:
            # 在形态识别之后，执行常规策略逻辑
            if self.dataclose[0] > self.dataclose[-1]:
                print(f"BUY SIGNAL at {bar['datetime']}")
                self.buy()
