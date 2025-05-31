import polars as pl
import os

# 正確的動態庫路徑
LIB = os.path.join(
    os.path.dirname(__file__), "target/release/libpolars_indicator.dylib"
)


def register_plugin_function(
    args,
    plugin_path,
    function_name: str,
    is_elementwise: bool = True,
):
    """註冊插件函數的輔助函數"""
    return pl.plugins.register_plugin_function(
        plugin_path=plugin_path,
        function_name=function_name,
        args=args,
        is_elementwise=is_elementwise,
    )


def atr(high, low, close, period: int = 14) -> pl.Expr:
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
    high,
    low,
    close,
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
    high,
    low,
    close,
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


if __name__ == "__main__":
    # 示範資料 - 增加到20筆以滿足ATR計算需求
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

    # 計算所有指標
    df_with_indicators = df.with_columns(
        atr("high", "low", "close", 14).alias("atr_14"),
        supertrend("high", "low", "close", 14, 3.0).alias("supertrend"),
        supertrend_direction("high", "low", "close", 14, 3.0).alias("direction"),
    )

    print("\n包含所有指標的資料:")
    print(df_with_indicators)
