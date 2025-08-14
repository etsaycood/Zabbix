import requests
import pandas as pd
import time

url = "http://192.168.168.3/api_jsonrpc.php"
headers = {
    "Authorization": "Bearer 6a08efe1a5a5db0b3719627c50e20b51139e4e1389c71ca699f9099c768c04b3",
    "Content-Type": "application/json-rpc"
}
# Linux
# Step 1: Get CPU itemid
hostid = "10084"
host = "acer"
item_data = {
    "jsonrpc": "2.0",
    "method": "item.get",
    "params": {
        "hostids": hostid,
        "search": {"name": "CPU idle time"},
        "output": ["itemid", "name", "key_"]
    },
    "id": 1
}
item_resp = requests.post(url, headers=headers, json=item_data).json()
if not item_resp['result']:
    print("No CPU itemid")
else:
    cpu_itemid = item_resp['result'][0]['itemid']
# Step 2: Get 30 days of historical data
now = int(time.time())
oneweek = now - 7*24*60*60
history_data = {
    "jsonrpc": "2.0",
    "method": "history.get",
    "params": {
        "history": 0,  # float
        "itemids": cpu_itemid,
        "time_from": oneweek,
        "time_till": now,
        "output": "extend"
    },
    "id": 2
}
history_resp = requests.post(url, headers=headers, json=history_data).json()
history_list = history_resp['result']

# Step 3: Export to CSV
if history_list:
    df = pd.DataFrame(history_list)
    df['clock'] = pd.to_datetime(df['clock'], unit='s')
    #Change the value to 100 - idle
    df['value'] = 100-df['value'].astype(float)
    df.to_csv(f'{host}-cpu_history.csv', index=False)
    print("cpu_history.csv has been exported")
else:
    print("No historical data found")

# Memory    
item_data = {
    "jsonrpc": "2.0",
    "method": "item.get",
    "params": {
        "hostids": hostid,
        "search": {"name": "Memory utilization"},
        "output": ["itemid", "name", "key_"]
    },
    "id": 3
}
item_resp = requests.post(url, headers=headers, json=item_data).json()
if not item_resp['result']:
    print("No Memory itemid")
else:
    mem_itemid = item_resp['result'][0]['itemid']
    # Get 7 days of historical data
    oneweek = now - 7*24*60*60
    history_data = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "history": 0,  # float
            "itemids": mem_itemid,
            "time_from": oneweek,
            "time_till": now,
            "output": "extend"
        },
        "id": 2
    }
    history_resp = requests.post(url, headers=headers, json=history_data).json()
    history_list = history_resp['result']

    # Step 3: Export to CSV
    if history_list:
        df = pd.DataFrame(history_list)
        df['clock'] = pd.to_datetime(df['clock'], unit='s')
        df.to_csv(f'{host}-mem_history.csv', index=False)
        print("mem_history.csv has been exported")
    else:
        print("No historical data found")