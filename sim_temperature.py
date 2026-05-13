import requests, time, random, math

ORION = "http://localhost:1026/v2"
ENTITY_ID = "urn:ngsi-ld:TemperatureSensor:kitchen-01"
HEADERS = {"Content-Type": "application/json"}

def update(attrs):
    url = f"{ORION}/entities/{ENTITY_ID}/attrs"
    r = requests.patch(url, json=attrs, headers=HEADERS)
    print(f"[TempSensor] {attrs} → {r.status_code}")

def heat_index(T, H):
    # Simplified Steadman formula
    hi = -8.78469475556 + 1.61139411*T + 2.33854883889*H \
         - 0.14611605*T*H - 0.012308094*T**2 \
         - 0.0164248277778*H**2 + 0.002211732*T**2*H \
         + 0.00072546*T*H**2 - 0.000003582*T**2*H**2
    return round(hi, 2)

tick = 0
base_temp = 22.0
base_humidity = 55.0

while True:
    tick += 1
    # Slow drift with random noise — realistic sensor behaviour
    base_temp += random.uniform(-0.05, 0.08)
    base_temp = max(18.0, min(35.0, base_temp))
    base_humidity += random.uniform(-0.3, 0.3)
    base_humidity = max(30.0, min(90.0, base_humidity))

    temp = round(base_temp + random.uniform(-0.2, 0.2), 2)
    humidity = round(base_humidity + random.uniform(-1, 1), 2)
    hi = heat_index(temp, humidity)

    update({
        "temperature": {"value": temp,     "type": "Number"},
        "humidity":    {"value": humidity, "type": "Number"},
        "heatIndex":   {"value": hi,       "type": "Number"}
    })
    time.sleep(5)
