#!/usr/bin/env python3
"""
Position Processing Example

This example demonstrates how to use the position processing functions
to clean trading signals and manage position IDs.
"""

import polars as pl
from polars_indicator import (
    clean_enex_position,
    reshape_position_id_array,
)


def main():
    print("=== Position Processing Example ===\n")

    # 創建包含交易信號的示例數據
    print("1. Creating sample trading signals...")
    df = pl.DataFrame(
        {
            "timestamp": range(10),
            "entry": [
                False,
                True,
                True,
                False,
                False,
                False,
                True,
                False,
                False,
                False,
            ],
            "exit": [False, False, False, True, True, False, False, False, True, False],
            "price": [
                100.0,
                101.0,
                102.0,
                103.0,
                104.0,
                105.0,
                106.0,
                107.0,
                108.0,
                109.0,
            ],
        }
    )

    print("Original signals:")
    print(df)
    print()

    # 清理交易信號
    print("2. Cleaning trading signals...")
    result = df.with_columns(clean_enex_position("entry", "exit", True).struct.unnest())

    print("Cleaned signals:")
    print(result)
    print()

    # 展示 entry_first=False 的情況
    print("3. Cleaning with entry_first=False...")
    result_exit_first = df.with_columns(
        clean_enex_position("entry", "exit", False).struct.unnest()
    )

    print("Cleaned signals (exit first):")
    print(result_exit_first)
    print()

    # 展示 reshape_position_id_array 功能
    print("4. Demonstrating reshape_position_id_array...")
    trades_df = pl.DataFrame(
        {
            "trade_id": [0, 1, 2],
            "entry_idx": [1, 6, 15],
            "exit_idx": [3, 8, 18],
        }
    )

    print("Trades data:")
    print(trades_df)
    print()

    # 將交易數據重塑為與 OHLCV 數據長度一致的位置ID數組
    position_array = trades_df.select(
        reshape_position_id_array(
            20, "trade_id", "entry_idx", "exit_idx"  # OHLCV 數據長度
        ).alias("position_array")
    )

    print("Reshaped position array (length=20):")
    print(position_array)
    print()

    # 展示位置數組的內容
    positions = position_array["position_array"].to_list()
    print("Position array values:")
    for i, pos in enumerate(positions):
        status = "In position" if pos >= 0 else "No position"
        print(f"Index {i:2d}: Position {pos:2d} ({status})")
    print()

    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
