from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from polars.plugins import register_plugin_function

from polars_indicator._internal import __version__ as __version__

if TYPE_CHECKING:
    from polars_indicator.typing import IntoExprColumn

LIB = Path(__file__).parent


def pig_latinnify(expr: IntoExprColumn) -> pl.Expr:
    return register_plugin_function(
        args=[expr],
        plugin_path=LIB,
        function_name="pig_latinnify",
        is_elementwise=True,
    )


def atr(
    high: IntoExprColumn,
    low: IntoExprColumn,
    close: IntoExprColumn,
    period: int = 14,
) -> pl.Expr:
    """
    計算 Average True Range (ATR)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: ATR 計算期間，預設為 14

    Returns:
        ATR 值的 Polars 表達式
    """
    return register_plugin_function(
        args=[high, low, close, pl.lit(period)],
        plugin_path=LIB,
        function_name="atr",
        is_elementwise=False,
    )


def supertrend(
    high: IntoExprColumn,
    low: IntoExprColumn,
    close: IntoExprColumn,
    atr_period: int = 14,
    multiplier: float = 3.0,
) -> pl.Expr:
    """
    計算 SuperTrend 趨勢線

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        atr_period: ATR 計算期間，預設為 14
        multiplier: ATR 倍數，預設為 3.0

    Returns:
        SuperTrend 趨勢線值
    """
    return register_plugin_function(
        args=[high, low, close, pl.lit(atr_period), pl.lit(multiplier)],
        plugin_path=LIB,
        function_name="supertrend",
        is_elementwise=False,
    )


def supertrend_direction(
    high: IntoExprColumn,
    low: IntoExprColumn,
    close: IntoExprColumn,
    atr_period: int = 14,
    multiplier: float = 3.0,
) -> pl.Expr:
    """
    計算 SuperTrend 方向

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        atr_period: ATR 計算期間，預設為 14
        multiplier: ATR 倍數，預設為 3.0

    Returns:
        SuperTrend 方向 (1 為看漲, -1 為看跌)
    """
    return register_plugin_function(
        args=[high, low, close, pl.lit(atr_period), pl.lit(multiplier)],
        plugin_path=LIB,
        function_name="supertrend_direction",
        is_elementwise=False,
    )


def clean_enex_position_ids(
    entries: IntoExprColumn,
    exits: IntoExprColumn,
    entry_first: bool = True,
) -> pl.Expr:
    """
    清理進場和出場信號數組，返回位置ID

    Args:
        entries: 進場信號數組，可能包含連續的 True 值
        exits: 出場信號數組，可能包含連續的 True 值
        entry_first: 當進場和出場信號同時出現時的優先順序，預設為 True

    Returns:
        每個時間點對應的位置ID
    """
    return register_plugin_function(
        args=[entries, exits, pl.lit(entry_first)],
        plugin_path=LIB,
        function_name="clean_enex_position",
        is_elementwise=False,
    )


def clean_entries(
    entries: IntoExprColumn,
    exits: IntoExprColumn,
    entry_first: bool = True,
) -> pl.Expr:
    """
    清理進場信號

    Args:
        entries: 進場信號數組，可能包含連續的 True 值
        exits: 出場信號數組，可能包含連續的 True 值
        entry_first: 當進場和出場信號同時出現時的優先順序，預設為 True

    Returns:
        清理後的進場信號
    """
    return register_plugin_function(
        args=[entries, exits, pl.lit(entry_first)],
        plugin_path=LIB,
        function_name="clean_entries",
        is_elementwise=False,
    )


def clean_exits(
    entries: IntoExprColumn,
    exits: IntoExprColumn,
    entry_first: bool = True,
) -> pl.Expr:
    """
    清理出場信號

    Args:
        entries: 進場信號數組，可能包含連續的 True 值
        exits: 出場信號數組，可能包含連續的 True 值
        entry_first: 當進場和出場信號同時出現時的優先順序，預設為 True

    Returns:
        清理後的出場信號
    """
    return register_plugin_function(
        args=[entries, exits, pl.lit(entry_first)],
        plugin_path=LIB,
        function_name="clean_exits",
        is_elementwise=False,
    )


def reshape_position_id_array(
    ohlcv_lens: int,
    position_id_arr: IntoExprColumn,
    entry_idx_arr: IntoExprColumn,
    exit_idx_arr: IntoExprColumn,
) -> pl.Expr:
    """
    從 trades 建立 position_id array

    Args:
        ohlcv_lens: 需與 ohlcv 長度相符
        position_id_arr: 長度與 trades 一致的位置ID數組
        entry_idx_arr: 長度與 trades 一致的進場索引數組
        exit_idx_arr: 長度與 trades 一致的出場索引數組

    Returns:
        長度與 ohlcv 一致的位置ID數組
    """
    return register_plugin_function(
        args=[
            pl.lit(ohlcv_lens),
            position_id_arr,
            entry_idx_arr,
            exit_idx_arr,
        ],
        plugin_path=LIB,
        function_name="reshape_position_id_array",
        is_elementwise=False,
    )
