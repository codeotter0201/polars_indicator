from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import polars as pl
from polars.plugins import register_plugin_function

from polars_indicator._internal import __version__ as __version__

if TYPE_CHECKING:
    from polars_indicator.typing import IntoExprColumn

LIB = Path(__file__).parent

__all__ = [
    "pig_latinnify",
    "supertrend",
    "clean_enex_position",
    "reshape_position_id_array",
]


def pig_latinnify(expr: IntoExprColumn) -> pl.Expr:
    return register_plugin_function(
        args=[expr],
        plugin_path=LIB,
        function_name="pig_latinnify",
        is_elementwise=True,
    )


def supertrend(
    high: IntoExprColumn = pl.col("high"),
    low: IntoExprColumn = pl.col("low"),
    close: IntoExprColumn = pl.col("close"),
    atr: IntoExprColumn = pl.col("atr"),
    upper_multiplier: float = 2.0,
    lower_multiplier: float = 2.0,
) -> pl.Expr:
    """
    計算 SuperTrend 指標

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        atr: ATR 值序列
        upper_multiplier: 上軌倍數，預設為 2.0
        lower_multiplier: 下軌倍數，預設為 2.0

    Returns:
        包含 direction, long, short, trend 四個字段的結構體表達式
    """
    # 註冊插件函數以獲取結構
    st_struct = register_plugin_function(
        args=[
            high,
            low,
            close,
            atr,
            pl.lit(upper_multiplier),
            pl.lit(lower_multiplier),
        ],
        plugin_path=LIB,
        function_name="supertrend",
        is_elementwise=False,
    )

    # atr_str = atr.meta.output_name()

    return st_struct.alias("supertrend")


def clean_enex_position(
    entries: IntoExprColumn,
    exits: IntoExprColumn,
    entry_first: bool = True,
) -> pl.Expr:
    """
    清理進場和出場信號數組，返回包含清理後信號和位置ID的結構體

    Args:
        entries: 進場信號數組，可能包含連續的 True 值
        exits: 出場信號數組，可能包含連續的 True 值
        entry_first: 當進場和出場信號同時出現時的優先順序，預設為 True

    Returns:
        包含 entries_out, exits_out, positions_out 三個字段的結構體表達式
    """
    return register_plugin_function(
        args=[entries, exits, pl.lit(entry_first)],
        plugin_path=LIB,
        function_name="clean_enex_position",
        is_elementwise=False,
    ).alias("clean_enex_position")


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
