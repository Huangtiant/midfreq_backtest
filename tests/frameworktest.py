# run_backtest.py

import sys
import os
import backtrader as bt
import pandas as pd

# === 动态添加项目根路径，以便跨目录引用 ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategies.BOM_identification.bom_strategy import BOMStrategy


def run_for_day(day_df, day_str):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BOMStrategy)

    # 如果缺少 volume 列，则补上默认值
    if 'volume' not in day_df.columns:
        day_df['volume'] = 0

    # 转换为 backtrader 数据格式
    data = bt.feeds.PandasData(dataname=day_df)

    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)

    print(f"=== Backtest for {day_str} ===")
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print("============================================")


def run_daily_backtests():
    # 读取大 CSV 文件
    df = pd.read_csv('data/raw/ES_5min.csv', parse_dates=True, index_col='time')

    # 按照日期分组
    grouped = df.groupby(df.index.date)

    for day, day_df in grouped:
        run_for_day(day_df, str(day))


if __name__ == '__main__':
    run_daily_backtests()
