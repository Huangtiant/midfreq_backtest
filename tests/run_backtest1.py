# run_backtest.py

import sys
import os
import backtrader as bt
import pandas as pd

# === 动态添加项目根路径，以便跨目录引用 ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategies.BOM_identificaiton.bom_strategy import BOMStrategy


def run():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BOMStrategy)

    # 读取 CSV 数据
    df = pd.read_csv('data/raw/ES_5min.csv', parse_dates=True, index_col='time')

    # 如果缺少 volume 列，则补上默认值
    if 'volume' not in df.columns:
        df['volume'] = 0

    # 转换为 backtrader 数据格式
    data = bt.feeds.PandasData(dataname=df)

    # 加入数据
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 打印初始资金
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 运行策略
    cerebro.run()

    # 打印结束资金
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 绘图（可选）
    cerebro.plot()


if __name__ == '__main__':
    run()
