# utils/data_loader.py
"""
轻量级行情 DataLoader

- 支持按 ‘symbol_timeframe.csv’ 或直接文件名加载
- 自动解析带时区的 time 列，转成 DatetimeIndex
- 所有数值列转为 float64，支持后续技术指标计算
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd


class DataLoader:
    """
    Example
    -------
    >>> loader = DataLoader(data_dir="../data")           # data/raw/ES_5min.csv
    >>> df = loader.load_csv("es", timeframe="5min")     # 或 loader.load_csv("myfile.csv")
    >>> df.head()  # doctest: +SKIP

                     open     high      low    close  hourly_20_ema      plot
    2025-06-06 15:30:00+00:00  ...
    """

    def __init__(
        self,
        data_dir: str | Path = "data",
        raw_subdir: str = "raw",
        default_tz: str = "UTC",
    ) -> None:
        self.data_dir = Path(data_dir)
        self.raw_path = self.data_dir / raw_subdir
        self.default_tz = default_tz

    # ---------- public API -------------------------------------------------

    @functools.lru_cache(maxsize=32)
    def load_csv(
        self,
        symbol_or_file: str,
        *,
        timeframe: str | None = None,
        usecols: Iterable[str] | None = None,
        dropna: bool = True,
        dtype_map: Mapping[str, str] | None = None,
    ) -> pd.DataFrame:
        """
        Parameters
        ----------
        symbol_or_file : str
            - "ES" + timeframe="1h"  ->  data/raw/ES_1h.csv
            - "BTC_USD_5min.csv"     ->  data/raw/BTC_USD_5min.csv
        timeframe : str, optional
            若指定则自动拼接文件名；否则直接把 symbol_or_file 当文件名
        usecols : list-like[str], optional
            只读取指定列；默认 None 读取全部
        dropna : bool
            是否在加载后 `df.dropna()`（默认 True）
        dtype_map : dict[str, str], optional
            显式指定某些列的 dtype；其余数值列自动转 float64
        """
        file_path = self._resolve_path(symbol_or_file, timeframe)
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        # --- 读入 ----------------------------------------------------------
        df = pd.read_csv(
            file_path,
            parse_dates=["time"],
            usecols=usecols,          # None = 全部
            dtype=dtype_map,          # 先用显式映射
        )

        # --- 标准化 column 名（全小写去空格） ------------------------------
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

        # --- ensure tz-aware ----------------------------------------------
        if df["time"].dt.tz is None:
            df["time"] = df["time"].dt.tz_localize(self.default_tz)

        df = df.set_index("time").sort_index()

        # --- 剩余列统一转 float64 ------------------------------------------
        for col in df.columns:
            if df[col].dtype.kind not in {"f", "i"}:  # 不是 float / int
                df[col] = pd.to_numeric(df[col], errors="ignore")
        if dropna:
            df.dropna(how="all", inplace=True)

        return df

    # ---------- helpers ----------------------------------------------------

    def _resolve_path(self, symbol_or_file: str, timeframe: str | None) -> Path:
        """
        生成完整的文件路径：
        - 有 timeframe 时：  {raw}/{symbol}_{timeframe}.csv
        - 否则：            {raw}/{symbol_or_file}
        """
        if timeframe:
            filename = f"{symbol_or_file}_{timeframe}.csv"
        else:
            filename = symbol_or_file if symbol_or_file.endswith(".csv") else f"{symbol_or_file}.csv"
        return self.raw_path / filename
