# test_data_loader.py
import pytest
import pandas as pd
from pathlib import Path
from utils.data_loader import DataLoader
import shutil

# 测试目录结构
TEST_DIR = Path("test_data")
RAW_PATH = TEST_DIR / "raw"


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """创建测试目录和CSV样本"""
    RAW_PATH.mkdir(parents=True, exist_ok=True)

    # 样本数据 1 (带时区)
    data1 = """time,Open,High,Low,Close
2023-01-01 09:30:00+00:00,100.0,101.5,99.8,101.0
2023-01-01 09:35:00+00:00,101.0,102.0,100.5,101.5"""
    (RAW_PATH / "ES_5min.csv").write_text(data1)

    # 样本数据 2 (无时区 + 空格列名)
    data2 = """time, Open Price, High Price, Volume
2023-01-01 10:00:00,150.25,151.75,1200
2023-01-01 10:05:00,151.0,152.5,1500"""
    (RAW_PATH / "BTC_1h.csv").write_text(data2)

    # 样本数据 3 (带空值)
    data3 = """time,open,high,low,close
2023-01-01 11:00:00+00:00,200,,,
2023-01-01 11:05:00+00:00,201,202.5,200.5,202"""
    (RAW_PATH / "NQ_15min.csv").write_text(data3)

    yield  # 执行测试

    # 清理测试目录
    shutil.rmtree(TEST_DIR)


# ----- 测试路径解析 -----
def test_path_resolution_with_timeframe():
    loader = DataLoader(data_dir=TEST_DIR)
    path = loader._resolve_path("ES", "5min")
    assert path == RAW_PATH / "ES_5min.csv"


def test_path_resolution_without_timeframe():
    loader = DataLoader(data_dir=TEST_DIR)
    path = loader._resolve_path("special_data.csv", None)
    assert path == RAW_PATH / "special_data.csv"


# ----- 测试核心加载功能 -----
def test_basic_loading():
    loader = DataLoader(data_dir=TEST_DIR)
    df = loader.load_csv("ES", timeframe="5min")

    # 验证基础结构
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "time"
    assert list(df.columns) == ["open", "high", "low", "close"]

    # 验证数据类型
    assert all(df.dtypes == "float64")

    # 验证时区
    assert str(df.index[0].tz) == "UTC"


def test_column_normalization():
    loader = DataLoader(data_dir=TEST_DIR)
    df = loader.load_csv("BTC", timeframe="1h")

    # 验证列名标准化
    assert list(df.columns) == ["open_price", "high_price", "volume"]

    # 验证数值转换
    assert df["volume"].dtype == "int64"  # 自动转整数


def test_timezone_handling():
    loader = DataLoader(data_dir=TEST_DIR, default_tz="Asia/Shanghai")
    df = loader.load_csv("BTC", timeframe="1h")

    # 验证自动添加时区
    assert str(df.index[0].tz) == "Asia/Shanghai"


def test_dropna_behavior():
    loader = DataLoader(data_dir=TEST_DIR)
    df = loader.load_csv("NQ", timeframe="15min")

    # 验证空值行被移除
    assert len(df) == 1
    assert df.iloc[0]["close"] == 202.0


def test_usecols_and_dtype_map():
    loader = DataLoader(data_dir=TEST_DIR)
    df = loader.load_csv("ES", timeframe="5min",
                         usecols=["time", "open", "close"],
                         dtype_map={"open": "int32"})

    # 验证列筛选
    assert list(df.columns) == ["open", "close"]

    # 验证 dtype 强制转换
    assert df["open"].dtype == "int32"


# ----- 测试缓存功能 -----
def test_lru_caching():
    loader = DataLoader(data_dir=TEST_DIR)

    # 首次加载（应缓存）
    df1 = loader.load_csv("ES", timeframe="5min")

    # 篡改源数据
    original_data = (RAW_PATH / "ES_5min.csv").read_text()
    (RAW_PATH / "ES_5min.csv").write_text("time,open\n2023-01-01,999")

    # 再次加载（应返回缓存）
    df2 = loader.load_csv("ES", timeframe="5min")

    # 恢复文件
    (RAW_PATH / "ES_5min.csv").write_text(original_data)

    # 验证缓存一致性
    pd.testing.assert_frame_equal(df1, df2)


# ----- 测试异常处理 -----
def test_file_not_found():
    loader = DataLoader(data_dir=TEST_DIR)
    with pytest.raises(FileNotFoundError):
        loader.load_csv("INVALID", timeframe="1d")