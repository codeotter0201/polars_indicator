import polars as pl
from polars_indicator import atr, supertrend, supertrend_direction


def test_atr():
    """測試 ATR 計算函數"""
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

    result = df.with_columns(atr_14=atr("high", "low", "close", 14))

    # 檢查基本結構
    assert "atr_14" in result.columns
    assert result.height == 15

    # 檢查前13個值為null（因為需要14個期間）
    atr_values = result.select("atr_14").to_series().to_list()
    for i in range(13):
        assert atr_values[i] is None

    # 檢查第14個值不為null且為正數
    assert atr_values[13] is not None
    assert atr_values[13] > 0


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

    result = df.with_columns(supertrend_val=supertrend("high", "low", "close", 14, 3.0))

    # 檢查基本結構
    assert "supertrend_val" in result.columns
    assert result.height == 15

    # 檢查前13個值為null
    st_values = result.select("supertrend_val").to_series().to_list()
    for i in range(13):
        assert st_values[i] is None

    # 檢查第14個值不為null且為正數
    assert st_values[13] is not None
    assert st_values[13] > 0


def test_supertrend_direction():
    """測試 SuperTrend 方向計算函數"""
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

    result = df.with_columns(
        direction=supertrend_direction("high", "low", "close", 14, 3.0)
    )

    # 檢查基本結構
    assert "direction" in result.columns
    assert result.height == 15

    # 檢查前13個值為null
    dir_values = result.select("direction").to_series().to_list()
    for i in range(13):
        assert dir_values[i] is None

    # 檢查第14個值不為null且為1或-1
    assert dir_values[13] is not None
    assert dir_values[13] in [1, -1]


def test_supertrend_all_indicators():
    """測試所有SuperTrend指標一起計算"""
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

    result = df.with_columns(
        atr("high", "low", "close", 14).alias("atr_14"),
        supertrend("high", "low", "close", 14, 3.0).alias("supertrend"),
        supertrend_direction("high", "low", "close", 14, 3.0).alias("direction"),
    )

    # 檢查所有欄位都存在
    expected_columns = [
        "high",
        "low",
        "close",
        "atr_14",
        "supertrend",
        "direction",
    ]
    for col in expected_columns:
        assert col in result.columns

    # 檢查資料型別
    assert result.select("atr_14").dtypes[0] == pl.Float64
    assert result.select("supertrend").dtypes[0] == pl.Float64
    assert result.select("direction").dtypes[0] == pl.Int32

    # 檢查最後幾個值不為null（有足夠資料計算）
    last_row = result.tail(1)
    assert last_row["atr_14"].item() is not None
    assert last_row["supertrend"].item() is not None
    assert last_row["direction"].item() is not None


def test_supertrend_empty_dataframe():
    """測試空DataFrame的處理"""
    df = pl.DataFrame(
        {
            "high": [],
            "low": [],
            "close": [],
        },
        schema={"high": pl.Float64, "low": pl.Float64, "close": pl.Float64},
    )

    result = df.with_columns(
        atr("high", "low", "close", 14).alias("atr_14"),
        supertrend("high", "low", "close", 14, 3.0).alias("supertrend"),
        supertrend_direction("high", "low", "close", 14, 3.0).alias("direction"),
    )

    # 應該能正常處理空DataFrame
    assert result.height == 0
    assert "atr_14" in result.columns
    assert "supertrend" in result.columns
    assert "direction" in result.columns
