import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk məlumatları GitHub Secrets-dən götürülür
SPLUNK_HOST = os.environ["SPLUNK_HOST"]
SPLUNK_USER = os.environ["SPLUNK_USER"]
SPLUNK_PASS = os.environ["SPLUNK_PASS"]

API_URL = f"{SPLUNK_HOST}/servicesNS/nobody/search/saved/searches"


# rules.json faylını oxuyuruq
try:
    with open("rules.json", "r", encoding="utf-8") as f:
        rules = json.load(f)

except json.JSONDecodeError as e:
    print("ERROR: rules.json düzgün JSON formatında deyil.")
    print(f"Line: {e.lineno}")
    print(f"Column: {e.colno}")
    print(f"Message: {e.msg}")
    raise


# Qaydaları Splunk-a göndəririk
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

    response = requests.post(
        endpoint,
        data=payload,
        auth=(SPLUNK_USER, SPLUNK_PASS),
        verify=False
    )

    if response.status_code in [200, 201]:
        print(f"[SUCCESS] Rule yeniləndi: {rule_name}")

    else:
        payload["name"] = rule_name

        create_resp = requests.post(
            API_URL,
            data=payload,
            auth=(SPLUNK_USER, SPLUNK_PASS),
            verify=False
        )

        if create_resp.status_code in [200, 201]:
            print(f"[CREATED] Rule yaradıldı: {rule_name}")
        else:
            print(
                f"[ERROR] {rule_name}: "
                f"{create_resp.status_code} - {create_resp.text}"
            )
