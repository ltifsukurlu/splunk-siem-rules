import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk REST API Məlumatları
SPLUNK_HOST = "https://64.177.46.110:8089"
SPLUNK_USER = "admin"
SPLUNK_PASS = "Mill1?ecspl."  # Bura öz Splunk admin parolunu yaz

API_URL = f"{SPLUNK_HOST}/servicesNS/nobody/search/saved/searches"

# rules.json faylını oxuyur
with open("rules.json", "r") as f:
    rules = json.load(f)

for rule_name, rule_data in rules.items():
    payload = {
        "search": rule_data["search"],
        "action.email": "1",
        "action.email.to": "letifsukurlu144@gmail.com",
        "alert.suppress": "1",
        "alert.suppress.period": "5m",
        "alert.track": "1",
        "is_scheduled": "1",
        "cron_schedule": "* * * * *"
    }
    
    endpoint = f"{API_URL}/{rule_name}"
    response = requests.post(endpoint, data=payload, auth=(SPLUNK_USER, SPLUNK_PASS), verify=False)
    
    if response.status_code in [200, 201]:
        print(f"[SUCCESS] Rule yeniləndi: {rule_name}")
    else:
        payload["name"] = rule_name
        create_resp = requests.post(API_URL, data=payload, auth=(SPLUNK_USER, SPLUNK_PASS), verify=False)
        if create_resp.status_code in [200, 201]:
            print(f"[CREATED] Rule yaradıldı: {rule_name}")
        else:
            print(f"[ERROR] {rule_name}: {create_resp.status_code}")
