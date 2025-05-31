#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;

// SuperTrend 計算函數 - 返回結構包含 direction, long, short, trend
#[polars_expr(output_type_func=supertrend_output_type)]
fn supertrend(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &inputs[0];
    let low = &inputs[1];
    let close = &inputs[2];
    let atr = &inputs[3];
    let upper_multiplier = &inputs[4];
    let lower_multiplier = &inputs[5];

    let high_ca: &Float64Chunked = high.f64()?;
    let low_ca: &Float64Chunked = low.f64()?;
    let close_ca: &Float64Chunked = close.f64()?;
    let atr_ca: &Float64Chunked = atr.f64()?;
    let upper_mult = upper_multiplier.f64()?.get(0).unwrap_or(3.0);
    let lower_mult = lower_multiplier.f64()?.get(0).unwrap_or(3.0);

    let len = high_ca.len();

    let mut direction_values = Vec::with_capacity(len);
    let mut long_values = Vec::with_capacity(len);
    let mut short_values = Vec::with_capacity(len);
    let mut trend_values = Vec::with_capacity(len);

    let mut prev_direction = 1i32;
    let mut prev_upper_band = 0.0f64;
    let mut prev_lower_band = 0.0f64;

    for i in 0..len {
        let h = high_ca.get(i);
        let l = low_ca.get(i);
        let c = close_ca.get(i);
        let atr_val = atr_ca.get(i);

        // 處理 None 或 NaN 值
        let h_valid = h.filter(|&x| !x.is_nan());
        let l_valid = l.filter(|&x| !x.is_nan());
        let c_valid = c.filter(|&x| !x.is_nan());
        let atr_valid = atr_val.filter(|&x| !x.is_nan());

        if h_valid.is_none() || l_valid.is_none() || c_valid.is_none() || atr_valid.is_none() {
            direction_values.push(None);
            long_values.push(None);
            short_values.push(None);
            trend_values.push(None);
            continue;
        }

        let h = h_valid.unwrap();
        let l = l_valid.unwrap();
        let c = c_valid.unwrap();
        let atr_val = atr_valid.unwrap();

        let hl2 = (h + l) / 2.0;
        let mut upper_band = hl2 + (upper_mult * atr_val);
        let mut lower_band = hl2 - (lower_mult * atr_val);

        // 計算最終的 bands
        if i > 0 {
            let c_prev = close_ca.get(i - 1);
            let c_prev_valid = c_prev.filter(|&x| !x.is_nan());
            if c_prev_valid.is_none() {
                // 如果前一個 close 是 None 或 NaN，當前值也應該是 None
                direction_values.push(None);
                long_values.push(None);
                short_values.push(None);
                trend_values.push(None);
                continue;
            }
            let c_prev = c_prev_valid.unwrap();

            if upper_band < prev_upper_band || c_prev > prev_upper_band {
                // 保持上軌
            } else {
                upper_band = prev_upper_band;
            }

            if lower_band > prev_lower_band || c_prev < prev_lower_band {
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

        // 設定 long 和 short 值
        let long = if direction > 0 {
            Some(lower_band)
        } else {
            None
        };
        let short = if direction < 0 {
            Some(upper_band)
        } else {
            None
        };

        direction_values.push(Some(direction));
        long_values.push(long);
        short_values.push(short);
        trend_values.push(Some(trend));

        prev_direction = direction;
        prev_upper_band = upper_band;
        prev_lower_band = lower_band;
    }

    let direction = Int32Chunked::new("direction".into(), direction_values);
    let long = Float64Chunked::new("long".into(), long_values);
    let short = Float64Chunked::new("short".into(), short_values);
    let trend = Float64Chunked::new("trend".into(), trend_values);

    Ok(StructChunked::from_series(
        "supertrend".into(),
        len,
        vec![
            direction.into_series(),
            long.into_series(),
            short.into_series(),
            trend.into_series(),
        ]
        .iter(),
    )?
    .into_series())
}

fn supertrend_output_type(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("direction".into(), DataType::Int32),
        Field::new("long".into(), DataType::Float64),
        Field::new("short".into(), DataType::Float64),
        Field::new("trend".into(), DataType::Float64),
    ];
    Ok(Field::new("supertrend".into(), DataType::Struct(fields)))
}
