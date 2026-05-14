import requests
import time
import random
import datetime

# ---------------- CONFIG ----------------
ORION = "http://localhost:1026/v2"
HEADERS = {"Content-Type": "application/json"}

ENTITIES = {
    "plug": "urn:ngsi-ld:SmartPlug:living-room-01",
    "camera": "urn:ngsi-ld:Camera:front-door-01",
    "tv": "urn:ngsi-ld:SmartTV:bedroom-01",
    "meter": "urn:ngsi-ld:SmartMeter:main-01",
    "temp": "urn:ngsi-ld:TemperatureSensor:kitchen-01"
}

APPS = ["Netflix", "YouTube", "Hotstar", "Prime Video"]

# ---------------- COMMON FUNCTION ----------------
def update(entity_id, attrs):
    url = f"{ORION}/entities/{entity_id}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"{entity_id} -> {r.status_code}")


# ---------------- TEMPERATURE SENSOR ----------------
base_temp = 22.0
base_humidity = 55.0

def heat_index(T, H):
    hi = -8.78469475556 + 1.61139411*T + 2.33854883889*H \
         - 0.14611605*T*H - 0.012308094*T**2 \
         - 0.0164248277778*H**2
    return round(hi, 2)


# ---------------- SMART TV STATE ----------------
tv_state = "off"
tv_channel = 1
tv_volume = 20
tv_app = "none"

# ---------------- SMART METER STATE ----------------
kwh_today = 0.0

# ---------------- MAIN LOOP ----------------
tick = 0

while True:
    tick += 1

    # =================================================
    # SMART PLUG
    # =================================================
    plug_on = (tick % 45) < 30

    update(ENTITIES["plug"], {
        "state": {
            "value": "on" if plug_on else "off",
            "type": "Text"
        },
        "power_w": {
            "value": round(random.uniform(800, 1200), 2) if plug_on else 0,
            "type": "Number"
        },
        "voltage_v": {
            "value": round(random.uniform(228, 232), 1),
            "type": "Number"
        }
    })

    # =================================================
    # CAMERA
    # =================================================
    motion = random.random() < 0.2
    recording = motion or random.random() < 0.1

    update(ENTITIES["camera"], {
        "motionDetected": {
            "value": motion,
            "type": "Boolean"
        },
        "recording": {
            "value": recording,
            "type": "Boolean"
        },
        "fps": {
            "value": round(random.uniform(24, 30), 1) if recording else 0,
            "type": "Number"
        }
    })

    # =================================================
    # SMART TV
    # =================================================
    if tick % 60 == 0:
        tv_state = "on" if tv_state == "off" else "off"

    if tv_state == "on":

        if random.random() < 0.1:
            tv_channel = random.randint(1, 100)

        if random.random() < 0.05:
            tv_app = random.choice(APPS)

        tv_volume = max(0, min(100, tv_volume + random.randint(-5, 5)))

    update(ENTITIES["tv"], {
        "state": {
            "value": tv_state,
            "type": "Text"
        },
        "channel": {
            "value": tv_channel,
            "type": "Number"
        },
        "volume": {
            "value": tv_volume,
            "type": "Number"
        },
        "app": {
            "value": tv_app,
            "type": "Text"
        }
    })

    # =================================================
    # SMART METER
    # =================================================
    hour = datetime.datetime.now().hour

    base_kw = random.uniform(1.5, 3.5) if 7 <= hour <= 22 else random.uniform(0.2, 0.8)

    current_kw = round(base_kw, 3)

    kwh_today += current_kw * 5 / 3600

    update(ENTITIES["meter"], {
        "kwh_today": {
            "value": round(kwh_today, 4),
            "type": "Number"
        },
        "current_kw": {
            "value": current_kw,
            "type": "Number"
        },
        "voltage_v": {
            "value": round(random.uniform(228, 232), 1),
            "type": "Number"
        },
        "tariff": {
            "value": "day" if 6 <= hour <= 22 else "night",
            "type": "Text"
        }
    })

    # =================================================
    # TEMPERATURE SENSOR
    # =================================================
    base_temp += random.uniform(-0.05, 0.05)
    base_humidity += random.uniform(-0.3, 0.3)

    temp = round(base_temp, 2)
    humidity = round(base_humidity, 2)

    update(ENTITIES["temp"], {
        "temperature": {
            "value": temp,
            "type": "Number"
        },
        "humidity": {
            "value": humidity,
            "type": "Number"
        },
        "heatIndex": {
            "value": heat_index(temp, humidity),
            "type": "Number"
        }
    })

    print("------------------------------------------------")

    time.sleep(5)
