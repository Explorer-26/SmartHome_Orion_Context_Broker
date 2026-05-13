import requests, time, random, datetime

ORION = "http://localhost:1026/v2"
ENTITY_ID = "urn:ngsi-ld:SmartMeter:main-01"
HEADERS = {"Content-Type": "application/json"}

def update(attrs):
    url = f"{ORION}/entities/{ENTITY_ID}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"[Meter] {attrs} → {r.status_code}")

kwh_today = 0.0

while True:
    hour = datetime.datetime.now().hour
    # Daytime: higher load; night: lower
    base_kw = random.uniform(1.5, 3.5) if 7 <= hour <= 22 else random.uniform(0.2, 0.8)
    current_kw = round(base_kw + random.uniform(-0.2, 0.2), 3)
    kwh_today = round(kwh_today + (current_kw * 5 / 3600), 4)  # 5 sec interval
    voltage = round(random.uniform(228, 232), 1)
    tariff = "day" if 6 <= hour <= 22 else "night"

    update({
        "kwh_today":  {"value": kwh_today,  "type": "Number"},
        "current_kw": {"value": current_kw, "type": "Number"},
        "voltage_v":  {"value": voltage,    "type": "Number"},
        "tariff":     {"value": tariff,     "type": "Text"}
    })
    time.sleep(5)
