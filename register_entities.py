import requests

ORION = "http://localhost:1026/v2"
HEADERS = {"Content-Type": "application/json"}

entities = [
    {
        "id": "urn:ngsi-ld:SmartPlug:living-room-01",
        "type": "SmartPlug",
        "state":       {"value": "off",  "type": "Text"},
        "power_w":     {"value": 0.0,    "type": "Number"},
        "voltage_v":   {"value": 230.0,  "type": "Number"},
        "location":    {"value": "Living Room", "type": "Text"}
    },
    {
        "id": "urn:ngsi-ld:Camera:front-door-01",
        "type": "Camera",
        "motionDetected": {"value": False, "type": "Boolean"},
        "recording":      {"value": False, "type": "Boolean"},
        "fps":            {"value": 25,    "type": "Number"},
        "location":       {"value": "Front Door", "type": "Text"}
    },
    {
        "id": "urn:ngsi-ld:SmartTV:bedroom-01",
        "type": "SmartTV",
        "state":   {"value": "off",  "type": "Text"},
        "channel": {"value": 1,      "type": "Number"},
        "volume":  {"value": 20,     "type": "Number"},
        "app":     {"value": "none", "type": "Text"},
        "location":{"value": "Bedroom", "type": "Text"}
    },
    {
        "id": "urn:ngsi-ld:SmartMeter:main-01",
        "type": "SmartMeter",
        "kwh_today":   {"value": 0.0,   "type": "Number"},
        "current_kw":  {"value": 0.0,   "type": "Number"},
        "voltage_v":   {"value": 230.0, "type": "Number"},
        "tariff":      {"value": "day", "type": "Text"},
        "location":    {"value": "Utility Room", "type": "Text"}
    },
    {
        "id": "urn:ngsi-ld:TemperatureSensor:kitchen-01",
        "type": "TemperatureSensor",
        "temperature": {"value": 22.0, "type": "Number"},
        "humidity":    {"value": 55.0, "type": "Number"},
        "heatIndex":   {"value": 22.0, "type": "Number"},
        "location":    {"value": "Kitchen", "type": "Text"}
    }
]

for e in entities:
    r = requests.post(f"{ORION}/entities", json=e, headers=HEADERS)
    if r.status_code in (201, 422):
        status = "created" if r.status_code == 201 else "already exists"
        print(f"[{status}] {e['id']}")
    else:
        print(f"[ERROR {r.status_code}] {e['id']}: {r.text}")
