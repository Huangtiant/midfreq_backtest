# utils/bom.py

def recognize_BOM(dataframe):
    """
    检查是否存在BOM形态。
    参数: dataframe：pandas.DataFrame格式的历史K线数据
    返回: True or False
    """
    # 开盘10-12根k是否组成BOM
    # 1.范围在30%-50%平均范围
    # 2.是否在第一根k线后交替创造新高新低（主要高低点）
    last = dataframe.iloc[-3:]
    # 假设形态条件是：中间K线最低
    if last['low'].iloc[1] < last['low'].iloc[0] and last['low'].iloc[1] < last['low'].iloc[2]:
        return True
    return False
