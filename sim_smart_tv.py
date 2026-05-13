import requests, time, random

ORION = "http://localhost:1026/v2"
ENTITY_ID = "urn:ngsi-ld:SmartTV:bedroom-01"
HEADERS = {"Content-Type": "application/json"}

APPS = ["Netflix", "YouTube", "Hotstar", "Prime Video", "none"]
CHANNELS = list(range(1, 100))

def update(attrs):
    url = f"{ORION}/entities/{ENTITY_ID}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"[SmartTV] {attrs} → {r.status_code}")

state = "off"
channel = 1
volume = 20
app = "none"
tick = 0

while True:
    tick += 1
    # Toggle on/off every 60 ticks (~5 minutes)
    if tick % 60 == 0:
        state = "on" if state == "off" else "off"

    if state == "on":
        # Occasionally change channel or app
        if random.random() < 0.1:
            channel = random.choice(CHANNELS)
            app = "none"
        if random.random() < 0.05:
            app = random.choice(APPS[:-1])
            channel = 0
        if random.random() < 0.1:
            volume = max(0, min(100, volume + random.randint(-5, 5)))

    update({
        "state":   {"value": state,   "type": "Text"},
        "channel": {"value": channel, "type": "Number"},
        "volume":  {"value": volume,  "type": "Number"},
        "app":     {"value": app,     "type": "Text"}
    })
    time.sleep(5)
