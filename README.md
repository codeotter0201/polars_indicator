# Polars Indicator

一個高效能的 Polars 插件，使用 Rust 實現技術指標計算，提供 Python 友好的 API。

## 特色

- 🚀 **高效能**: Rust 後端實現，效能優異
- 🐍 **Python 友好**: 無縫整合 Polars DataFrame API
- 🔧 **易於使用**: 簡潔直觀的函數介面
- ✅ **經過驗證**: 完整的測試覆蓋和邊界條件處理
- 📈 **專業級**: 支援複雜的交易信號處理

## 安裝

```bash
 polars as pl
pip install polars-indicator

# 開發環境安裝
uv run maturin develop
```

## 快速開始

### SuperTrend 指標

```python
import polars as pl
from polars_indicator import atr, supertrend, supertrend_direction

# 創建市場數據
df = pl.DataFrame({
    "high": [102.0, 103.5, 104.2, 103.8, 105.1],
    "low": [100.2, 101.8, 102.1, 101.9, 103.2],
    "close": [101.5, 102.8, 103.1, 102.9, 104.2],
})

# 計算 SuperTrend 指標
result = df.with_columns([
    atr("high", "low", "close", 14).alias("atr"),
    supertrend("high", "low", "close", 14, 3.0).alias("supertrend"),
    supertrend_direction("high", "low", "close", 14, 3.0).alias("direction"),
])

print(result)
```

### 交易信號處理

```python
from polars_indicator import (
    clean_entries,
    clean_exits,
    clean_enex_position_ids
)

# 創建交易信號
df = pl.DataFrame({
    "entry": [False, True, True, False, False],
    "exit": [False, False, False, True, True],
})

# 清理信號並生成持倉ID
result = df.with_columns([
    clean_entries("entry", "exit", True).alias("clean_entry"),
    clean_exits("entry", "exit", True).alias("clean_exit"),
    clean_enex_position_ids("entry", "exit", True).alias("position_id"),
])

print(result)
```

## 可用函數

### 技術指標

- `atr(high, low, close, period=14)` - Average True Range
- `supertrend(high, low, close, atr_period=14, multiplier=3.0)` - SuperTrend 趨勢線
- `supertrend_direction(high, low, close, atr_period=14, multiplier=3.0)` - SuperTrend 方向

### 交易信號處理

- `clean_entries(entries, exits, entry_first=True)` - 清理進場信號
- `clean_exits(entries, exits, entry_first=True)` - 清理出場信號
- `clean_enex_position_ids(entries, exits, entry_first=True)` - 生成持倉 ID
- `reshape_position_id_array(ohlcv_lens, position_id_arr, entry_idx_arr, exit_idx_arr)` - 重塑持倉數組

## 範例

查看 `example_position.py` 了解完整的使用範例。

```bash
uv run python example_position.py
```

## 開發

詳細的開發指南請參閱 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)。

### 快速開發設置

```bash
# 編譯 Rust 代碼
uv run maturin develop

# 執行測試
uv run python -m pytest tests/ -v

# 代碼風格檢查
uv run python -m ruff check .
```

## 發佈到 PyPI

### 準備工作

在發佈之前，請確保已準備以下資訊：

#### 1. PyPI 帳戶設置

- 在 [PyPI](https://pypi.org) 註冊帳戶
- 在 [TestPyPI](https://test.pypi.org) 註冊帳戶（用於測試）
- 啟用雙因子驗證（2FA）
- 創建 API Token：
  - 登入 PyPI → Account Settings → API tokens
  - 創建 token 並保存（只會顯示一次）

#### 2. 本地環境配置

```bash
# 安裝發佈相關依賴
uv add twine --group dev

# 配置 PyPI 認證（推薦使用 API token）
# 方法 1: 使用 .pypirc 檔案
cat > ~/.pypirc << EOF
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-test-api-token-here
EOF

# 方法 2: 使用環境變數
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-api-token-here
```

#### 3. 專案檢查清單

- [ ] 更新版本號（在 `Cargo.toml` 中）
- [ ] 更新 `CHANGELOG.md` 或發佈說明
- [ ] 確保所有測試通過
- [ ] 檢查 `pyproject.toml` 配置正確
- [ ] 驗證 `README.md` 內容完整

### 發佈步驟

#### 僅構建（測試用）

```bash
# 僅構建 wheel，不發佈
uv run python build_and_publish.py --build-only
```

#### 發佈到 TestPyPI（測試環境）

```bash
# 構建並發佈到測試環境
uv run python build_and_publish.py

# 或手動指定 TestPyPI
uv run python -m twine upload --repository testpypi target/wheels/*.whl
```

#### 發佈到正式 PyPI

```bash
# 構建並發佈到正式環境
uv run python build_and_publish.py

# 驗證安裝
pip install polars-indicator
```

### 發佈腳本說明

`build_and_publish.py` 腳本提供以下功能：

1. **清理舊構建**：自動清理 `dist/` 和 `target/wheels/` 目錄
2. **構建 wheel**：使用 maturin 構建 Rust 擴展
3. **發佈到 PyPI**：使用 twine 上傳到 PyPI

```bash
# 顯示幫助
uv run python build_and_publish.py --help

# 僅構建
uv run python build_and_publish.py --build-only

# 構建並發佈
uv run python build_and_publish.py
```

### 發佈後驗證

```bash
# 檢查 PyPI 頁面
# https://pypi.org/project/polars-indicator/

# 測試安裝
pip install --upgrade polars-indicator

# 驗證功能
python -c "import polars_indicator; print('成功導入')"
```

### 常見問題

#### 認證失敗

- 確認 API token 正確設置
- 檢查 `.pypirc` 檔案格式
- 使用 `twine check` 驗證 wheel 檔案

#### 上傳失敗

- 確認版本號未與現有版本衝突
- 檢查 `pyproject.toml` 配置
- 驗證 wheel 檔案完整性

#### 權限問題

- 確認 PyPI 帳戶有專案上傳權限
- 對於新專案，首次上傳需要完整的專案權限

## 貢獻

歡迎貢獻！請閱讀 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 了解如何參與開發。

## 許可證

MIT License
