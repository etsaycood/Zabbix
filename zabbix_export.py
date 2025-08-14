import requests
import pandas as pd
import time
import argparse
import sys

def zabbix_api_request(url, token, method, params):
    """
    Sends a request to the Zabbix API.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json-rpc"
    }
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1 # ID can be arbitrary
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        if 'error' in result:
            print(f"Zabbix API Error: {result['error']['message']} - {result['error']['data']}", file=sys.stderr)
            sys.exit(1)
        return result['result']
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}", file=sys.stderr)
        sys.exit(1)

def get_item_id(url, token, host_id, item_key):
    """
    Get the item ID for a specific item key on a host.
    """
    params = {
        "hostids": host_id,
        "search": {"key_": item_key},
        "output": ["itemid", "name", "key_"]
    }
    items = zabbix_api_request(url, token, "item.get", params)
    if not items:
        print(f"Error: Could not find item with key '{item_key}' on host '{host_id}'.", file=sys.stderr)
        sys.exit(1)
    # Assuming the first found item is the correct one
    return items[0]['itemid']

def get_item_history(url, token, item_id, history_type):
    """
    Get one week of history for a specific item ID.
    """
    now = int(time.time())
    one_week_ago = now - (7 * 24 * 60 * 60)
    
    params = {
        "history": history_type,  # 0 for float, 3 for integer
        "itemids": item_id,
        "time_from": one_week_ago,
        "time_till": now,
        "output": "extend"
    }
    return zabbix_api_request(url, token, "history.get", params)

def main():
    """
    Main function to parse arguments and export Zabbix history.
    """
    parser = argparse.ArgumentParser(description="Export Zabbix item history to a CSV file.")
    parser.add_argument('--url', required=True, help="Zabbix API URL (e.g., http://zabbix.example.com/api_jsonrpc.php)")
    parser.add_argument('--token', required=True, help="Zabbix API authorization token.")
    parser.add_argument('--hostid', required=True, help="The host ID to query.")
    parser.add_argument('--itemkey', required=True, help="The item key to export history for (e.g., 'system.cpu.util').")
    parser.add_argument('--output', required=True, help="Output CSV file name (e.g., 'cpu_history.csv').")
    parser.add_argument('--type', required=True, type=int, choices=[0, 1, 2, 3, 4], help="History type (0: float, 1: char, 2: log, 3: unsigned int, 4: text).")

    args = parser.parse_args()

    print(f"Fetching item ID for key: {args.itemkey}")
    item_id = get_item_id(args.url, args.token, args.hostid, args.itemkey)
    print(f"Found item ID: {item_id}")

    print("Fetching item history...")
    history_list = get_item_history(args.url, args.token, item_id, args.type)

    if not history_list:
        print("No history data found for the specified item and time range.")
        return

    print(f"Found {len(history_list)} history records.")
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(history_list)
    # Convert Unix timestamp to datetime
    df['clock'] = pd.to_datetime(df['clock'], unit='s')
    
    # Reorder columns for better readability
    cols = ['clock', 'value', 'itemid', 'ns']
    df = df[[c for c in cols if c in df.columns]]

    df.to_csv(args.output, index=False)
    print(f"Successfully exported history to {args.output}")

if __name__ == "__main__":
    main()
