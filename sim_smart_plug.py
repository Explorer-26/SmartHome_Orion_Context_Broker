import requests, time, random, math

ORION = "http://localhost:1026/v2"
ENTITY_ID = "urn:ngsi-ld:SmartPlug:living-room-01"
HEADERS = {"Content-Type": "application/json"}

def update(attrs):
    url = f"{ORION}/entities/{ENTITY_ID}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"[SmartPlug] {attrs} → {r.status_code}")

cycle = 0
while True:
    cycle += 1
    # Simulate a realistic load cycle: on for 30s, off for 15s
    on = (cycle % 45) < 30
    power = round(random.uniform(800, 1200) if on else 0.0, 2)
    voltage = round(random.uniform(228, 232), 1)
    update({
        "state":     {"value": "on" if on else "off", "type": "Text"},
        "power_w":   {"value": power,   "type": "Number"},
        "voltage_v": {"value": voltage, "type": "Number"}
    })
    time.sleep(5)
