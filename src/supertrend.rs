#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;

// ATR 計算函數
#[polars_expr(output_type=Float64)]
fn atr(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &inputs[0];
    let low = &inputs[1];
    let close = &inputs[2];
    let period = &inputs[3];

    let high_ca: &Float64Chunked = high.f64()?;
    let low_ca: &Float64Chunked = low.f64()?;
    let close_ca: &Float64Chunked = close.f64()?;
    let period_value = period.i32()?.get(0).unwrap_or(14) as usize;

    let len = high_ca.len();
    if len == 0 {
        return Ok(Float64Chunked::new("atr".into(), Vec::<Option<f64>>::new()).into_series());
    }

    let mut atr_values = Vec::with_capacity(len);
    let mut tr_sum = 0.0f64;
    let mut count = 0usize;

    for i in 0..len {
        let h = high_ca.get(i).unwrap_or(0.0);
        let l = low_ca.get(i).unwrap_or(0.0);
        let c_prev = if i > 0 {
            close_ca.get(i - 1).unwrap_or(0.0)
        } else {
            h
        };

        // 計算 True Range
        let tr = (h - l).max((h - c_prev).abs()).max((l - c_prev).abs());

        if i < period_value {
            // 初始期間：簡單平均
            tr_sum += tr;
            count += 1;
            if i == period_value - 1 {
                atr_values.push(Some(tr_sum / count as f64));
            } else {
                atr_values.push(None);
            }
        } else {
            // 使用 Wilder's Moving Average
            let prev_atr = atr_values[i - 1].unwrap_or(0.0);
            let atr = (prev_atr * (period_value - 1) as f64 + tr) / period_value as f64;
            atr_values.push(Some(atr));
        }
    }

    Ok(Float64Chunked::new("atr".into(), atr_values).into_series())
}

// SuperTrend 計算函數 - 回傳趨勢線
#[polars_expr(output_type=Float64)]
fn supertrend(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &inputs[0];
    let low = &inputs[1];
    let close = &inputs[2];
    let atr_period = &inputs[3];
    let multiplier = &inputs[4];

    let high_ca: &Float64Chunked = high.f64()?;
    let low_ca: &Float64Chunked = low.f64()?;
    let close_ca: &Float64Chunked = close.f64()?;
    let atr_period_value = atr_period.i32()?.get(0).unwrap_or(14) as usize;
    let multiplier_value = multiplier.f64()?.get(0).unwrap_or(3.0);

    let len = high_ca.len();
    if len == 0 {
        return Ok(
            Float64Chunked::new("supertrend".into(), Vec::<Option<f64>>::new()).into_series(),
        );
    }

    // 先計算 ATR
    let mut atr_values = Vec::with_capacity(len);
    let mut tr_sum = 0.0f64;
    let mut count = 0usize;

    for i in 0..len {
        let h = high_ca.get(i).unwrap_or(0.0);
        let l = low_ca.get(i).unwrap_or(0.0);
        let c_prev = if i > 0 {
            close_ca.get(i - 1).unwrap_or(0.0)
        } else {
            h
        };

        let tr = (h - l).max((h - c_prev).abs()).max((l - c_prev).abs());

        if i < atr_period_value {
            tr_sum += tr;
            count += 1;
            if i == atr_period_value - 1 {
                atr_values.push(Some(tr_sum / count as f64));
            } else {
                atr_values.push(None);
            }
        } else {
            let prev_atr = atr_values[i - 1].unwrap_or(0.0);
            let atr = (prev_atr * (atr_period_value - 1) as f64 + tr) / atr_period_value as f64;
            atr_values.push(Some(atr));
        }
    }

    // 計算 SuperTrend
    let mut trend_values = Vec::with_capacity(len);
    let mut prev_direction = 1i32;
    let mut prev_upper_band = 0.0f64;
    let mut prev_lower_band = 0.0f64;

    for i in 0..len {
        let h = high_ca.get(i).unwrap_or(0.0);
        let l = low_ca.get(i).unwrap_or(0.0);
        let c = close_ca.get(i).unwrap_or(0.0);

        if let Some(atr) = atr_values[i] {
            let hl2 = (h + l) / 2.0;
            let mut upper_band = hl2 + (multiplier_value * atr);
            let mut lower_band = hl2 - (multiplier_value * atr);

            // 計算最終的 bands
            if i > 0 {
                if upper_band < prev_upper_band
                    || close_ca.get(i - 1).unwrap_or(0.0) > prev_upper_band
                {
                    // 保持上軌
                } else {
                    upper_band = prev_upper_band;
                }

                if lower_band > prev_lower_band
                    || close_ca.get(i - 1).unwrap_or(0.0) < prev_lower_band
                {
                    // 保持下軌
                } else {
                    lower_band = prev_lower_band;
                }
            }

            // 確定方向
            let direction = if i == 0 {
                1
            } else if c > prev_upper_band {
                1
            } else if c < prev_lower_band {
                -1
            } else {
                prev_direction
            };

            // 如果方向改變，調整 bands
            if direction != prev_direction {
                if direction > 0 && lower_band < prev_lower_band {
                    lower_band = prev_lower_band;
                }
                if direction < 0 && upper_band > prev_upper_band {
                    upper_band = prev_upper_band;
                }
            }

            // 確定趨勢線
            let trend = if direction > 0 {
                lower_band
            } else {
                upper_band
            };

            trend_values.push(Some(trend));
            prev_direction = direction;
            prev_upper_band = upper_band;
            prev_lower_band = lower_band;
        } else {
            trend_values.push(None);
        }
    }

    Ok(Float64Chunked::new("supertrend".into(), trend_values).into_series())
}

// SuperTrend 方向計算函數
#[polars_expr(output_type=Int32)]
fn supertrend_direction(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &inputs[0];
    let low = &inputs[1];
    let close = &inputs[2];
    let atr_period = &inputs[3];
    let multiplier = &inputs[4];

    let high_ca: &Float64Chunked = high.f64()?;
    let low_ca: &Float64Chunked = low.f64()?;
    let close_ca: &Float64Chunked = close.f64()?;
    let atr_period_value = atr_period.i32()?.get(0).unwrap_or(14) as usize;
    let multiplier_value = multiplier.f64()?.get(0).unwrap_or(3.0);

    let len = high_ca.len();
    if len == 0 {
        return Ok(Int32Chunked::new("direction".into(), Vec::<Option<i32>>::new()).into_series());
    }

    // 先計算 ATR
    let mut atr_values = Vec::with_capacity(len);
    let mut tr_sum = 0.0f64;
    let mut count = 0usize;

    for i in 0..len {
        let h = high_ca.get(i).unwrap_or(0.0);
        let l = low_ca.get(i).unwrap_or(0.0);
        let c_prev = if i > 0 {
            close_ca.get(i - 1).unwrap_or(0.0)
        } else {
            h
        };

        let tr = (h - l).max((h - c_prev).abs()).max((l - c_prev).abs());

        if i < atr_period_value {
            tr_sum += tr;
            count += 1;
            if i == atr_period_value - 1 {
                atr_values.push(Some(tr_sum / count as f64));
            } else {
                atr_values.push(None);
            }
        } else {
            let prev_atr = atr_values[i - 1].unwrap_or(0.0);
            let atr = (prev_atr * (atr_period_value - 1) as f64 + tr) / atr_period_value as f64;
            atr_values.push(Some(atr));
        }
    }

    // 計算 SuperTrend 方向
    let mut direction_values = Vec::with_capacity(len);
    let mut prev_direction = 1i32;
    let mut prev_upper_band = 0.0f64;
    let mut prev_lower_band = 0.0f64;

    for i in 0..len {
        let h = high_ca.get(i).unwrap_or(0.0);
        let l = low_ca.get(i).unwrap_or(0.0);
        let c = close_ca.get(i).unwrap_or(0.0);

        if let Some(atr) = atr_values[i] {
            let hl2 = (h + l) / 2.0;
            let mut upper_band = hl2 + (multiplier_value * atr);
            let mut lower_band = hl2 - (multiplier_value * atr);

            if i > 0 {
                if upper_band < prev_upper_band
                    || close_ca.get(i - 1).unwrap_or(0.0) > prev_upper_band
                {
                } else {
                    upper_band = prev_upper_band;
                }

                if lower_band > prev_lower_band
                    || close_ca.get(i - 1).unwrap_or(0.0) < prev_lower_band
                {
                } else {
                    lower_band = prev_lower_band;
                }
            }

            let direction = if i == 0 {
                1
            } else if c > prev_upper_band {
                1
            } else if c < prev_lower_band {
                -1
            } else {
                prev_direction
            };

            direction_values.push(Some(direction));
            prev_direction = direction;
            prev_upper_band = upper_band;
            prev_lower_band = lower_band;
        } else {
            direction_values.push(None);
        }
    }

    Ok(Int32Chunked::new("direction".into(), direction_values).into_series())
}
