import polars as pl
from polars_indicator import atr, supertrend, supertrend_direction


# 測試資料
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
            112.1,
            113.5,
            112.8,
            114.2,
            113.6,
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
            110.3,
            111.8,
            110.9,
            112.5,
            111.9,
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
            111.5,
            112.9,
            111.8,
            113.7,
            112.8,
        ],
    }
)

print("原始資料:")
print(df)

# 使用簡潔的 import 方式計算指標
result = df.with_columns(
    atr("high", "low", "close", 14).alias("atr_14"),
    supertrend("high", "low", "close", 14, 3.0).alias("supertrend"),
    supertrend_direction("high", "low", "close", 14, 3.0).alias("direction"),
)

print("\n包含 SuperTrend 指標的資料:")
print(result)
