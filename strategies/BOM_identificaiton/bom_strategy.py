# strategies/BOM_identificaiton/bom_strategy.py

import backtrader as bt
import pandas as pd
from utils.bom import recognize_BOM

class BOMStrategy(bt.Strategy):
    """
    识别BOM形态后再激活的交易策略。
    """

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.df_buffer = []  # 存储历史K线数据
        self.active = False  # 初始未识别出BOM
        self.order = None

    def next(self):
        bar = {
            'datetime': self.datas[0].datetime.datetime(0),
            'open': self.datas[0].open[0],
            'high': self.datas[0].high[0],
            'low': self.datas[0].low[0],
            'close': self.datas[0].close[0],
        }
        self.df_buffer.append(bar)

        if len(self.df_buffer) < 10:
            return

        df = pd.DataFrame(self.df_buffer)

        if not self.active:
            if recognize_BOM(df):
                print(f"BOM recognized at {bar['datetime']}")
                self.active = True
            else:
                return  # 没识别出BOM，不做任何操作

        # === 以下填写正式策略逻辑 ===
        # TODO: 写入你在识别BOM之后的交易逻辑
        pass
