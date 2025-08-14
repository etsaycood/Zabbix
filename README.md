# Zabbix 歷史資料匯出工具 (簡易版)

這是一個用於從 Zabbix API 匯出監控項目歷史資料到 CSV 檔案的 Python 腳本，專為快速展示和簡易使用而設計。

## 專案特點

- **簡單易用**: 無需複雜的命令列參數，直接執行腳本即可。
- **設定集中**: 所有 Zabbix 連線設定 (API URL, 權杖, 主機ID) 都集中在腳本檔案的最上方，方便修改。
- **功能明確**: 腳本會自動匯出預設的幾個關鍵指標 (CPU, 記憶體)，並存成不同的 CSV 檔案。

## 檔案結構

- `zabbix_simple_export.py`: **(主要執行檔)** 簡易版的匯出腳本。
- `requirements.txt`: 執行此腳本所需的 Python 套件。
- `zabbix_export.py`: (進階版) 一個功能更完整、使用命令列參數的匯出腳本。
- `old/`: 存放舊版 Jupyter Notebook 的存檔資料夾。

## 如何使用

### 1. 修改設定

在執行前，請先用文字編輯器打開 `zabbix_simple_export.py` 檔案，並修改最上方的設定區塊：

```python
# --- 設定 (請在此處修改) ---
ZABBIX_URL = "http://192.168.168.3/api_jsonrpc.php"
# 重要：請將下面的權杖換成您自己的
ZABBIX_TOKEN = "YOUR_SECRET_API_TOKEN"
HOST_ID = "10084"
# --- 設定結束 ---
```

### 2. 安裝依賴套件

在您的終端機中，執行以下指令來安裝 `requests` 和 `pandas`：

```bash
pip install -r requirements.txt
```

### 3. 執行腳本

安裝完套件後，直接執行腳本：

```bash
python zabbix_simple_export.py
```

腳本將會開始執行，並在同一個資料夾中建立數個 `demo_... .csv` 檔案。