# Polars Indicator 開發者指南

## 項目概述

這是一個高效能的 Polars 插件，使用 Rust 後端實現技術指標計算，並提供 Python 介面。本指南將幫助開發者快速理解項目架構並有效貢獻。

## 項目架構

### 整體結構

```
polars_indicator/
├── src/                    # Rust 後端實現
│   ├── lib.rs             # 模塊註冊和入口
│   ├── expressions.rs     # 基礎表達式函數
│   ├── supertrend.rs      # SuperTrend 指標實現
│   └── position.rs        # 持倉處理函數
├── polars_indicator/       # Python 介面
│   ├── __init__.py        # API 暴露和函數包裝
│   └── typing.py          # 類型定義
├── tests/                  # 測試套件
│   ├── test_supertrend.py # SuperTrend 測試
│   └── test_position.py   # 持倉處理測試
└── examples/              # 使用範例
```

### 雙層架構設計

- **Rust 後端**: 提供高效能計算核心
- **Python 介面**: 提供易用的 API 和 Polars 整合

## 核心開發理念

### 1. 效能優先

- 所有計算密集型操作都在 Rust 中實現
- 避免不必要的資料複製和轉換
- 使用 Polars 原生資料結構（ChunkedArray）

### 2. 類型安全

- Rust 端嚴格的類型檢查
- Python 端提供類型提示
- 參數驗證和錯誤處理

### 3. API 一致性

- 所有函數都遵循相同的命名規範
- 統一的參數傳遞模式
- 一致的錯誤處理策略

## 開發流程

### 1. 新增指標函數

#### Step 1: Rust 實現

```rust
// src/your_indicator.rs
#[polars_expr(output_type=Float64)]
fn your_indicator(inputs: &[Series]) -> PolarsResult<Series> {
    let input_series = &inputs[0];
    let param = &inputs[1];

    // 獲取 ChunkedArray
    let ca: &Float64Chunked = input_series.f64()?;
    let param_value = param.i32()?.get(0).unwrap_or(14);

    // 處理空數據
    let len = ca.len();
    if len == 0 {
        return Ok(Float64Chunked::new("result".into(), Vec::<Option<f64>>::new()).into_series());
    }

    // 實現計算邏輯
    let mut result = Vec::with_capacity(len);
    // ... 計算邏輯

    Ok(Float64Chunked::new("result".into(), result).into_series())
}
```

#### Step 2: 註冊模塊

```rust
// src/lib.rs
mod your_indicator;
```

#### Step 3: Python 介面

```python
# polars_indicator/__init__.py
def your_indicator(
    input_col: IntoExprColumn,
    param: int = 14,
) -> pl.Expr:
    """
    你的指標說明

    Args:
        input_col: 輸入序列
        param: 參數說明，預設為 14

    Returns:
        指標值的 Polars 表達式
    """
    return register_plugin_function(
        args=[input_col, pl.lit(param)],
        plugin_path=LIB,
        function_name="your_indicator",
        is_elementwise=False,  # 大多數指標都是 False
    )
```

### 2. 測試開發

#### 測試結構

```python
# tests/test_your_indicator.py
import polars as pl
from polars_indicator import your_indicator

class TestYourIndicator:
    def test_basic_functionality(self):
        """基本功能測試"""
        df = pl.DataFrame({
            "value": [1.0, 2.0, 3.0, 4.0, 5.0],
        })

        result = df.with_columns(
            indicator=your_indicator("value", 3)
        )

        assert "indicator" in result.columns
        assert result.height == 5

    def test_empty_dataframe(self):
        """空數據測試"""
        df = pl.DataFrame({
            "value": [],
        }, schema={"value": pl.Float64})

        result = df.with_columns(
            indicator=your_indicator("value", 3)
        )

        assert result.height == 0
        assert "indicator" in result.columns
```

## 關鍵技術要點

### 1. Polars 插件模式

#### 聚合 vs 元素級操作

```python
# 聚合操作（多行輸入，單一輸出）
df.select(your_agg_function("column").alias("result"))

# 元素級操作（逐行處理）
df.with_columns(your_element_function("column").alias("result"))
```

#### 函數註冊參數

```python
register_plugin_function(
    args=[input1, input2, pl.lit(param)],
    plugin_path=LIB,
    function_name="rust_function_name",
    is_elementwise=False,  # True 為元素級，False 為聚合
)
```

### 2. Rust 資料處理模式

#### ChunkedArray 操作

```rust
// 獲取特定類型的 ChunkedArray
let ca: &Float64Chunked = series.f64()?;
let bool_ca: &BooleanChunked = series.bool()?;
let int_ca: &Int64Chunked = series.i64()?;

// 安全地獲取值
let value = ca.get(i).unwrap_or(0.0);

// 建立結果
let result = Float64Chunked::new("name".into(), vec![1.0, 2.0, 3.0]);
```

#### 錯誤處理

```rust
// 空資料處理
if len == 0 {
    return Ok(Float64Chunked::new("result".into(), Vec::<Option<f64>>::new()).into_series());
}

// 參數驗證
let param_value = param_series.i32()?.get(0).unwrap_or(default_value);
```

### 3. 效能優化技巧

#### 記憶體預分配

```rust
let mut result = Vec::with_capacity(len);
```

#### 避免重複計算

```rust
// 緩存中間結果
let mut cache = vec![0.0; len];
for i in 0..len {
    if i == 0 {
        cache[i] = initial_value;
    } else {
        cache[i] = cache[i-1] * factor + new_value;
    }
}
```

## 代碼規範

### 1. Rust 規範

#### 命名規範

- 函數名: `snake_case`
- 變數名: `snake_case`
- 常數: `SCREAMING_SNAKE_CASE`

#### 代碼風格

```rust
// 使用 ? 操作符處理錯誤
let ca: &Float64Chunked = series.f64()?;

// 適當的空白和縮排
let result = if condition {
    value1
} else {
    value2
};

// 有意義的變數名
let moving_average = calculate_ma(&prices, period);
```

### 2. Python 規範

#### 類型提示

```python
def indicator_function(
    input_col: IntoExprColumn,
    period: int = 14,
) -> pl.Expr:
```

#### 文檔字串

```python
"""
指標功能說明

Args:
    input_col: 輸入序列說明
    period: 週期參數，預設為 14

Returns:
    指標值的 Polars 表達式
"""
```

#### 行長度限制

- 最大 79 字符
- 使用適當的換行和縮排

## 測試策略

### 1. 測試覆蓋範圍

- ✅ 基本功能測試
- ✅ 邊界條件測試（空數據、單個值）
- ✅ 參數驗證測試
- ✅ 錯誤處理測試
- ✅ 效能測試（大數據集）

### 2. 測試模式

```python
# 使用 select 進行聚合操作測試
result = df.select(agg_function("col").alias("result"))

# 使用 with_columns 進行逐行操作測試
result = df.with_columns(element_function("col").alias("result"))
```

### 3. 測試數據設計

```python
# 真實市場數據模擬
realistic_data = [100.5, 101.2, 99.8, 102.1, ...]

# 邊界條件
edge_cases = [0.0, float('inf'), float('-inf')]

# 特殊模式
special_patterns = [1, 1, 1, 1]  # 常數序列
```

## 常見問題和解決方案

### 1. 編譯錯誤

#### Polars 版本不相容

```rust
// 問題：使用了不支援的資料結構
// StructChunked 在某些版本不可用

// 解決：分別實現各個輸出
#[polars_expr(output_type=Int64)]
fn function_ids() -> PolarsResult<Series> { ... }

#[polars_expr(output_type=Boolean)]
fn function_flags() -> PolarsResult<Series> { ... }
```

#### 資料類型不匹配

```rust
// 確保輸入類型正確
let ca: &Float64Chunked = series.f64()?;
let int_value = int_series.i32()?.get(0).unwrap_or(0) as usize;
```

### 2. 測試錯誤

#### 聚合 vs 逐行操作混淆

```python
# 錯誤：聚合函數使用 with_columns
df.with_columns(agg_function("col"))  # ❌

# 正確：聚合函數使用 select
df.select(agg_function("col"))  # ✅
```

#### Linter 錯誤

```python
# 行太長
result = very_long_function_name("very_long_column_name", very_long_parameter)

# 修正：適當換行
result = very_long_function_name(
    "very_long_column_name",
    very_long_parameter
)
```

### 3. 效能問題

#### 避免不必要的資料複製

```rust
// 直接操作 ChunkedArray，避免轉換為 Vec
for i in 0..ca.len() {
    let value = ca.get(i).unwrap_or(0.0);
    // 處理
}
```

#### 選擇合適的資料結構

```rust
// 對於布林結果
BooleanChunked::new("result".into(), results)

// 對於數值結果
Float64Chunked::new("result".into(), results)
```

## 開發工具和命令

### 1. 建置和測試

```bash
# 編譯 Rust 代碼
uv run maturin develop

# 執行測試
uv run python -m pytest tests/

# 執行特定測試
uv run python -m pytest tests/test_position.py -v

# 代碼格式檢查
uv run python -m ruff check .
```

### 2. 範例執行

```bash
# 執行位置處理範例
uv run python example_position.py

# 建立新的範例
uv run python examples/your_example.py
```

## 貢獻指南

### 1. 開發流程

1. **Fork 項目**並建立功能分支
2. **實現 Rust 函數**並註冊模塊
3. **建立 Python 介面**和文檔
4. **撰寫全面測試**（至少 90% 覆蓋率）
5. **確保所有測試通過**
6. **檢查代碼風格**和 linter
7. **提交 Pull Request**

### 2. 提交規範

```bash
# 提交訊息格式
feat: add RSI indicator implementation
fix: handle empty dataframe in SuperTrend
docs: update developer guide for new patterns
test: add edge cases for position functions
```

### 3. Pull Request 檢查清單

- [ ] 所有測試通過
- [ ] 代碼符合風格規範
- [ ] 包含適當的文檔和範例
- [ ] 效能測試通過
- [ ] 向後相容性檢查

## 專案特色總結

### 1. 技術優勢

- **高效能**: Rust 實現的核心計算
- **易用性**: Python 友好的 API 設計
- **類型安全**: 全面的類型檢查和驗證
- **模塊化**: 清晰的架構和可擴展設計

### 2. 開發體驗

- **快速上手**: 清晰的範例和文檔
- **完整測試**: 全面的測試覆蓋和邊界條件
- **工具支援**: 完整的開發工具鏈
- **持續整合**: 自動化的品質檢查

這份指南涵蓋了所有關鍵的開發模式和最佳實踐。新的貢獻者應該能夠通過這份文檔快速理解項目架構並開始有效的開發工作。
