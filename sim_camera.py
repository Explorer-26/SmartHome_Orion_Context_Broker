import requests, time, random

ORION = "http://localhost:1026/v2"
ENTITY_ID = "urn:ngsi-ld:Camera:front-door-01"
HEADERS = {"Content-Type": "application/json"}

def update(attrs):
    url = f"{ORION}/entities/{ENTITY_ID}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"[Camera] {attrs} → {r.status_code}")

while True:
    # Random motion events, ~20% chance per tick
    motion = random.random() < 0.2
    # Recording starts when motion detected and stays on for a few cycles
    recording = motion or (random.random() < 0.1)
    fps = round(random.uniform(24, 30), 1) if recording else 0.0
    update({
        "motionDetected": {"value": motion,    "type": "Boolean"},
        "recording":      {"value": recording, "type": "Boolean"},
        "fps":            {"value": fps,        "type": "Number"}
    })
    time.sleep(3)
