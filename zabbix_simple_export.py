import requests
import pandas as pd
import time
import sys

# --- 設定 (請在此處修改) ---
ZABBIX_URL = "http://192.168.168.3/api_jsonrpc.php"
# 重要：請將下面的權杖換成您自己的，這裡使用的是您原始 Notebook 中的權杖
ZABBIX_TOKEN = "6a08efe1a5a5db0b3719627c50e20b51139e4e1389c71ca699f9099c768c04b3"
HOST_ID = "10084"
# --- 設定結束 ---

def zabbix_api_request(method, params):
    """Sends a request to the Zabbix API."""
    headers = {
        "Authorization": f"Bearer {ZABBIX_TOKEN}",
        "Content-Type": "application/json-rpc"
    }
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(ZABBIX_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        if 'error' in result:
            print(f"Zabbix API Error: {result['error']['message']} - {result['error']['data']}", file=sys.stderr)
            return None
        return result.get('result')
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}", file=sys.stderr)
        return None

def export_history(item_key, history_type, output_filename):
    """Fetches history for an item and exports it to a CSV file."""
    print(f"正在處理: {item_key}...")
    
    # 1. 取得 item ID
    item_params = {
        "hostids": HOST_ID,
        "search": {"key_": item_key},
        "output": ["itemid"]
    }
    items = zabbix_api_request("item.get", item_params)
    if not items:
        print(f"  -> 找不到 item key '{item_key}'")
        return

    item_id = items[0]['itemid']
    print(f"  -> 取得 Item ID: {item_id}")

    # 2. 取得歷史資料
    now = int(time.time())
    one_week_ago = now - (7 * 24 * 60 * 60)
    history_params = {
        "history": history_type,
        "itemids": item_id,
        "time_from": one_week_ago,
        "time_till": now,
        "output": "extend"
    }
    history_list = zabbix_api_request("history.get", history_params)

    if not history_list:
        print("  -> 查無歷史資料")
        return

    # 3. 匯出 CSV
    df = pd.DataFrame(history_list)
    df['clock'] = pd.to_datetime(df['clock'], unit='s')
    df.to_csv(output_filename, index=False)
    print(f"  -> 成功匯出 {len(df)} 筆資料到 {output_filename}")

def main():
    """主程式: 匯出指定的監控項目"""
    print("--- 開始匯出 Zabbix 歷史資料 ---")
    
    # 匯出 CPU 使用率 (float)
    export_history(item_key="system.cpu.util", history_type=0, output_filename="demo_cpu_util_history.csv")
    
    # 匯出可用記憶體百分比 (float)
    export_history(item_key="vm.memory.size[pavailable]", history_type=0, output_filename="demo_mem_pavailable_history.csv")

    # 匯出總記憶體 (integer)
    export_history(item_key="vm.memory.size[total]", history_type=3, output_filename="demo_mem_total_history.csv")

    print("--- 所有項目處理完畢 ---")

if __name__ == "__main__":
    main()
