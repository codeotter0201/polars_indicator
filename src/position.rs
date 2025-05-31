#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;

/// 清理進場和出場信號數組，處理交易的進場（entry）和出場（exit）信號
/// 返回包含 entries_out, exits_out, positions_out 三個字段的結構體
#[polars_expr(output_type_func=clean_enex_position_output_type)]
fn clean_enex_position(inputs: &[Series]) -> PolarsResult<Series> {
    let entries = &inputs[0];
    let exits = &inputs[1];
    let entry_first = &inputs[2];

    let entries_ca: &BooleanChunked = entries.bool()?;
    let exits_ca: &BooleanChunked = exits.bool()?;
    let entry_first_value = entry_first.bool()?.get(0).unwrap_or(true);

    let len = entries_ca.len();
    if len == 0 {
        let empty_bool = BooleanChunked::new("".into(), Vec::<Option<bool>>::new()).into_series();
        let empty_int64 = Int64Chunked::new("".into(), Vec::<Option<i64>>::new()).into_series();

        return Ok(StructChunked::from_series(
            "clean_enex_position".into(),
            0,
            vec![
                empty_bool.clone().with_name("entries_out".into()),
                empty_bool.with_name("exits_out".into()),
                empty_int64.with_name("positions_out".into()),
            ]
            .iter(),
        )?
        .into_series());
    }

    let mut entries_out = Vec::with_capacity(len);
    let mut exits_out = Vec::with_capacity(len);
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
                entries_out.push(Some(true));
                exits_out.push(Some(false));
                positions_out.push(Some(_position_id));
            } else {
                entries_out.push(Some(false));
                exits_out.push(Some(false));
                positions_out.push(Some(_position_id));
            }
        } else if exits_temp[i] {
            // 出場信號處理
            entries_out.push(Some(false));
            if phase == 1 {
                phase = 0;
                exits_out.push(Some(true));
                positions_out.push(Some(_position_id));
            } else {
                exits_out.push(Some(false));
                positions_out.push(Some(-1));
            }
        } else {
            // 維持當前狀態
            entries_out.push(Some(false));
            exits_out.push(Some(false));
            if phase == 1 {
                positions_out.push(Some(_position_id));
            } else {
                positions_out.push(Some(-1));
            }
        }
    }

    let entries_series = BooleanChunked::new("entries_out".into(), entries_out).into_series();
    let exits_series = BooleanChunked::new("exits_out".into(), exits_out).into_series();
    let positions_series = Int64Chunked::new("positions_out".into(), positions_out).into_series();

    Ok(StructChunked::from_series(
        "clean_enex_position".into(),
        len,
        vec![entries_series, exits_series, positions_series].iter(),
    )?
    .into_series())
}

fn clean_enex_position_output_type(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("entries_out".into(), DataType::Boolean),
        Field::new("exits_out".into(), DataType::Boolean),
        Field::new("positions_out".into(), DataType::Int64),
    ];
    Ok(Field::new(
        "clean_enex_position".into(),
        DataType::Struct(fields),
    ))
}

/// 從 trades 建立 _position_id array
#[polars_expr(output_type=Int64)]
fn reshape_position_id_array(inputs: &[Series]) -> PolarsResult<Series> {
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
