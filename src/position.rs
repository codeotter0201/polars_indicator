#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;

/// 清理進場和出場信號數組，處理交易的進場（entry）和出場（exit）信號
/// 這個函數實際上返回三個 Series：entries_out, exits_out, positions_out
/// 但由於 Polars 插件限制，我們只能返回一個 Series，所以我們返回 _position_id
#[polars_expr(output_type=Int64)]
fn clean_enex_position(inputs: &[Series]) -> PolarsResult<Series> {
    let entries = &inputs[0];
    let exits = &inputs[1];
    let entry_first = &inputs[2];

    let entries_ca: &BooleanChunked = entries.bool()?;
    let exits_ca: &BooleanChunked = exits.bool()?;
    let entry_first_value = entry_first.bool()?.get(0).unwrap_or(true);

    let len = entries_ca.len();
    if len == 0 {
        return Ok(
            Int64Chunked::new("positions_out".into(), Vec::<Option<i64>>::new()).into_series(),
        );
    }

    let mut positions_out = Vec::with_capacity(len);

    let mut phase = -1i32; // -1: 初始, 1: 已進場, 0: 已出場
    let mut _position_id = -1i64;

    // 複製輸入陣列以便修改
    let mut entries_temp: Vec<bool> = (0..len)
        .map(|i| entries_ca.get(i).unwrap_or(false))
        .collect();
    let mut exits_temp: Vec<bool> = (0..len).map(|i| exits_ca.get(i).unwrap_or(false)).collect();

    for i in 0..len {
        // 如果同時為 True 則以優先度選擇訊號
        if entries_temp[i] && exits_temp[i] {
            if entry_first_value {
                exits_temp[i] = false;
            } else {
                entries_temp[i] = false;
            }
        }

        // 處理進場信號
        if entries_temp[i] {
            if phase == -1 || phase == 0 {
                phase = 1;
                _position_id += 1;
                positions_out.push(Some(_position_id));
            } else {
                positions_out.push(Some(_position_id));
            }
        } else if exits_temp[i] {
            // 出場信號處理
            if phase == 1 {
                phase = 0;
                positions_out.push(Some(_position_id));
            } else {
                positions_out.push(Some(-1));
            }
        } else {
            // 維持當前狀態
            if phase == 1 {
                positions_out.push(Some(_position_id));
            } else {
                positions_out.push(Some(-1));
            }
        }
    }

    Ok(Int64Chunked::new("positions_out".into(), positions_out).into_series())
}

/// 從 trades 建立 _position_id array
#[polars_expr(output_type=Int64)]
fn reshape__position_id_array(inputs: &[Series]) -> PolarsResult<Series> {
    let ohlcv_lens = &inputs[0];
    let _position_id_arr = &inputs[1];
    let entry_idx_arr = &inputs[2];
    let exit_idx_arr = &inputs[3];

    let ohlcv_lens_value = ohlcv_lens.i32()?.get(0).unwrap_or(0) as usize;
    let _position_id_ca: &Int64Chunked = _position_id_arr.i64()?;
    let entry_idx_ca: &Int64Chunked = entry_idx_arr.i64()?;
    let exit_idx_ca: &Int64Chunked = exit_idx_arr.i64()?;

    let mut ret = vec![-1i64; ohlcv_lens_value];

    for i in 0.._position_id_ca.len() {
        if let (Some(pid), Some(entry_idx), Some(exit_idx)) = (
            _position_id_ca.get(i),
            entry_idx_ca.get(i),
            exit_idx_ca.get(i),
        ) {
            let entry_idx = entry_idx as usize;
            let exit_idx = exit_idx as usize;

            if entry_idx < ret.len() && exit_idx < ret.len() && entry_idx <= exit_idx {
                for j in entry_idx..=exit_idx {
                    ret[j] = pid;
                }
            }
        }
    }

    Ok(Int64Chunked::new("_position_id".into(), ret).into_series())
}

/// 清理進場信號 - 輔助函數
#[polars_expr(output_type=Boolean)]
fn clean_entries(inputs: &[Series]) -> PolarsResult<Series> {
    let entries = &inputs[0];
    let exits = &inputs[1];
    let entry_first = &inputs[2];

    let entries_ca: &BooleanChunked = entries.bool()?;
    let exits_ca: &BooleanChunked = exits.bool()?;
    let entry_first_value = entry_first.bool()?.get(0).unwrap_or(true);

    let len = entries_ca.len();
    if len == 0 {
        return Ok(
            BooleanChunked::new("entries_out".into(), Vec::<Option<bool>>::new()).into_series(),
        );
    }

    let mut entries_out = Vec::with_capacity(len);

    let mut phase = -1i32; // -1: 初始, 1: 已進場, 0: 已出場
    let mut _position_id = -1i64;

    // 複製輸入陣列以便修改
    let mut entries_temp: Vec<bool> = (0..len)
        .map(|i| entries_ca.get(i).unwrap_or(false))
        .collect();
    let mut exits_temp: Vec<bool> = (0..len).map(|i| exits_ca.get(i).unwrap_or(false)).collect();

    for i in 0..len {
        // 如果同時為 True 則以優先度選擇訊號
        if entries_temp[i] && exits_temp[i] {
            if entry_first_value {
                exits_temp[i] = false;
            } else {
                entries_temp[i] = false;
            }
        }

        // 處理進場信號
        if entries_temp[i] {
            if phase == -1 || phase == 0 {
                phase = 1;
                entries_out.push(Some(true));
                _position_id += 1;
            } else {
                entries_out.push(Some(false));
            }
        } else {
            entries_out.push(Some(false));
            if exits_temp[i] && phase == 1 {
                phase = 0;
            }
        }
    }

    Ok(BooleanChunked::new("entries_out".into(), entries_out).into_series())
}

/// 清理出場信號 - 輔助函數
#[polars_expr(output_type=Boolean)]
fn clean_exits(inputs: &[Series]) -> PolarsResult<Series> {
    let entries = &inputs[0];
    let exits = &inputs[1];
    let entry_first = &inputs[2];

    let entries_ca: &BooleanChunked = entries.bool()?;
    let exits_ca: &BooleanChunked = exits.bool()?;
    let entry_first_value = entry_first.bool()?.get(0).unwrap_or(true);

    let len = entries_ca.len();
    if len == 0 {
        return Ok(
            BooleanChunked::new("exits_out".into(), Vec::<Option<bool>>::new()).into_series(),
        );
    }

    let mut exits_out = Vec::with_capacity(len);

    let mut phase = -1i32; // -1: 初始, 1: 已進場, 0: 已出場
    let mut _position_id = -1i64;

    // 複製輸入陣列以便修改
    let mut entries_temp: Vec<bool> = (0..len)
        .map(|i| entries_ca.get(i).unwrap_or(false))
        .collect();
    let mut exits_temp: Vec<bool> = (0..len).map(|i| exits_ca.get(i).unwrap_or(false)).collect();

    for i in 0..len {
        // 如果同時為 True 則以優先度選擇訊號
        if entries_temp[i] && exits_temp[i] {
            if entry_first_value {
                exits_temp[i] = false;
            } else {
                entries_temp[i] = false;
            }
        }

        // 處理進場信號
        if entries_temp[i] {
            if phase == -1 || phase == 0 {
                phase = 1;
                _position_id += 1;
            }
        }

        // 處理出場信號
        if exits_temp[i] {
            if phase == 1 {
                phase = 0;
                exits_out.push(Some(true));
            } else {
                exits_out.push(Some(false));
            }
        } else {
            exits_out.push(Some(false));
        }
    }

    Ok(BooleanChunked::new("exits_out".into(), exits_out).into_series())
}
