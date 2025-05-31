import polars as pl
import polars_talib as plta
from polars_indicator import supertrend

# 創建示例數據
df = pl.DataFrame(
    {
        "high": [
            102.0,
            103.5,
            104.2,
            103.8,
            105.1,
            106.3,
            105.9,
            107.2,
            108.1,
            107.8,
            109.5,
            108.9,
            110.2,
            111.0,
            109.8,
        ],
        "low": [
            100.2,
            101.8,
            102.1,
            101.9,
            103.2,
            104.5,
            103.8,
            105.1,
            106.2,
            105.9,
            107.1,
            106.8,
            108.5,
            109.2,
            107.9,
        ],
        "close": [
            101.5,
            102.8,
            103.1,
            102.9,
            104.2,
            105.8,
            104.9,
            106.5,
            107.3,
            106.8,
            108.9,
            107.5,
            109.8,
            110.1,
            108.7,
        ],
    }
)

# 計算 ATR (使用簡單的方法)
df = df.lazy().with_columns(atr=plta.atr(timeperiod=7))

# 使用 supertrend 函數 - 返回 4 個欄位
result = df.with_columns(supertrend())

print("原始數據與 SuperTrend 結果:")
print(result.collect())

# 也可以使用自訂參數
result_custom = df.with_columns(
    supertrend(
        pl.col("high"),
        pl.col("low"),
        pl.col("close"),
        pl.col("atr"),
        upper_multiplier=2.0,
        lower_multiplier=2.0,
    )
)

print("\n使用自訂參數的 SuperTrend 結果:")
print(result_custom.collect())

# 顯示最後幾行的詳細資料
print("\n最後 5 行的詳細資料:")
print(
    result.select(
        pl.col("close"),
        pl.col("atr"),
        pl.col("supertrend").struct.field("direction"),
        pl.col("supertrend").struct.field("long"),
        pl.col("supertrend").struct.field("short"),
        pl.col("supertrend").struct.field("trend"),
    )
    .tail(5)
    .collect()
)
