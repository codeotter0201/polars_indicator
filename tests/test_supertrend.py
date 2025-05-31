import polars as pl
import polars_talib as plta
from polars_indicator import supertrend


def calculate_atr(df: pl.DataFrame, period: int = 14) -> pl.DataFrame:
    """輔助函數：計算 ATR"""
    return df.with_columns(atr=plta.atr(timeperiod=period))


def test_supertrend():
    """測試 SuperTrend 計算函數"""
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

    # 先計算 ATR
    df = calculate_atr(df, 14)

    # 計算 SuperTrend
    result = df.with_columns(supertrend())

    # 檢查基本結構 - 應該有supertrend結構體欄位
    assert "supertrend" in result.columns
    assert result.height == 15

    # 從結構體中提取字段
    expanded = result.with_columns(
        result["supertrend"].struct.field("direction").alias("direction"),
        result["supertrend"].struct.field("long").alias("long"),
        result["supertrend"].struct.field("short").alias("short"),
        result["supertrend"].struct.field("trend").alias("trend"),
    )

    # 檢查前14個值為null（因為 ATR 需要14個期間）
    direction_values = expanded.select("direction").to_series().to_list()
    for i in range(14):
        assert direction_values[i] is None

    # 檢查第15個值不為null（索引14）
    assert direction_values[14] is not None
    assert direction_values[14] in [1, -1]

    # 檢查 trend 值
    trend_values = expanded.select("trend").to_series().to_list()
    assert trend_values[14] is not None
    assert trend_values[14] > 0


def test_supertrend_custom_parameters():
    """測試自訂參數的 SuperTrend"""
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
            ],
        }
    )

    # 計算 ATR
    df = calculate_atr(df, 14)

    # 使用自訂參數計算 SuperTrend
    result = df.with_columns(
        supertrend(
            pl.col("high"),
            pl.col("low"),
            pl.col("close"),
            pl.col("atr"),
            upper_multiplier=2.0,
            lower_multiplier=2.0,
        )
    )

    # 檢查基本欄位都存在
    expected_columns = [
        "high",
        "low",
        "close",
        "atr",
        "supertrend",
    ]
    for col in expected_columns:
        assert col in result.columns

    # 從結構體中提取字段並檢查資料型別
    expanded = result.with_columns(
        result["supertrend"].struct.field("direction").alias("direction"),
        result["supertrend"].struct.field("long").alias("long"),
        result["supertrend"].struct.field("short").alias("short"),
        result["supertrend"].struct.field("trend").alias("trend"),
    )

    assert expanded.select("direction").dtypes[0] == pl.Int32
    assert expanded.select("long").dtypes[0] == pl.Float64
    assert expanded.select("short").dtypes[0] == pl.Float64
    assert expanded.select("trend").dtypes[0] == pl.Float64

    # 檢查最後幾個值不為null（有足夠資料計算）
    last_row = expanded.tail(1)
    assert last_row["direction"].item() is not None
    assert last_row["trend"].item() is not None


def test_supertrend_empty_dataframe():
    """測試空DataFrame的處理"""
    df = pl.DataFrame(
        {
            "high": [],
            "low": [],
            "close": [],
            "atr": [],
        },
        schema={
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "atr": pl.Float64,
        },
    )

    result = df.with_columns(supertrend())

    # 應該能正常處理空DataFrame
    assert result.height == 0
    assert "supertrend" in result.columns

    # 檢查結構體schema
    assert result.schema["supertrend"] == pl.Struct(
        {
            "direction": pl.Int32,
            "long": pl.Float64,
            "short": pl.Float64,
            "trend": pl.Float64,
        }
    )


def test_supertrend_with_nan():
    """測試包含 NaN 值的處理"""
    df = pl.DataFrame(
        {
            "high": [102.0, None, 104.2, 103.8, 105.1],
            "low": [100.2, 101.8, None, 101.9, 103.2],
            "close": [101.5, 102.8, 103.1, None, 104.2],
            "atr": [1.5, None, 1.8, 1.6, None],
        }
    )

    result = df.with_columns(supertrend())

    # 檢查基本結構
    assert "supertrend" in result.columns
    assert result.height == 5

    # 從結構體中提取direction字段
    expanded = result.with_columns(
        result["supertrend"].struct.field("direction").alias("direction")
    )

    # 當輸入有 NaN 時，對應位置應該是 null
    direction_values = expanded.select("direction").to_series().to_list()
    assert direction_values[1] is None  # atr 是 None
    assert direction_values[2] is None  # low 是 None
    assert direction_values[3] is None  # close 是 None
    assert direction_values[4] is None  # atr 是 None
