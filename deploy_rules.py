import os
import requests
import configparser
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk məlumatları GitHub Secrets-dən götürülür
SPLUNK_HOST = os.environ["SPLUNK_HOST"]
SPLUNK_USER = os.environ["SPLUNK_USER"]
SPLUNK_PASS = os.environ["SPLUNK_PASS"]

API_URL = f"{SPLUNK_HOST}/servicesNS/nobody/search/saved/searches"

rules_dir = "rules"

if not os.path.exists(rules_dir):
    print(f"XƏTA: '{rules_dir}' qovluğu tapılmadı!")
    exit(1)

for file_name in os.listdir(rules_dir):
    if file_name.endswith(".conf"):
        file_path = os.path.join(rules_dir, file_name)
        config = configparser.ConfigParser()
        
        try:
            config.read(file_path, encoding="utf-8")
        except Exception as e:
            print(f"[-] {file_name} faylı oxunarkən xəta yarandı: {e}")
            continue

        for section in config.sections():
            rule_name = section
            if config.has_option(section, "search"):
                search_query = config.get(section, "search")
            else:
                print(f"[-] {rule_name} üçün 'search' parametri tapılmadı.")
                continue

            payload = {
                "name": rule_name,
                "search": search_query,
                "is_scheduled": "1",
                "cron_schedule": "*/5 * * * *",
                "action.email": "1",
                "action.email.to": "letifsukurlu144@gmail.com",
                "action.email.useNSSubject": "1",
                "action.email.subject": f"Splunk Alert: {rule_name}",
                "action.email.format": "table",
                "action.email.sendresults": "1"
            }

            try:
                response = requests.post(
                    API_URL,
                    data=payload,
                    auth=(SPLUNK_USER, SPLUNK_PASS),
                    verify=False
                )

                if response.status_code in [200, 201]:
                    print(f"[+] Uğurla əlavə edildi: {rule_name} ({file_name})")
                elif response.status_code == 409:
                    print(f"[!] Qayda artıq mövcuddur: {rule_name}")
                else:
                    print(f"[-] Xəta ({response.status_code}) - {rule_name}: {response.text}")

            except Exception as e:
                print(f"[-] İstisna xətası ({rule_name}): {e}")
