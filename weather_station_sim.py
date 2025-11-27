# ==========================================
# Simulation IoT : Station météo virtuelle + Dashboard Plotly + Downlink
# ==========================================

!pip install paho-mqtt plotly

import time
import json
from random import uniform
from collections import deque

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import plotly.graph_objects as go
from IPython.display import display, clear_output

# ------------------ CONFIGURATION ------------------
MQTT_HOST = "broker.hivemq.com"   # Broker public gratuit
MQTT_PORT = 1883

DATA_TOPIC = "virtual_weather_station/telemetry"
CONTROL_TOPIC = "virtual_weather_station/control"

CLIENT_ID = "weather-station-sim-01"

# Modes : "normal" envoie plus souvent, "eco" envoie moins souvent
PUBLISH_INTERVAL_NORMAL = 4   # secondes
PUBLISH_INTERVAL_ECO = 10     # secondes

current_mode = "normal"
current_interval = PUBLISH_INTERVAL_NORMAL

# Seuil d’alerte température (modifiable par commande downlink)
TEMP_ALERT_THRESHOLD = 28.0

# Historique pour le dashboard
timestamps = deque(maxlen=30)
temperatures = deque(maxlen=30)
humidities = deque(maxlen=30)
pressures = deque(maxlen=30)       # on garde la pression dans les données, mais on ne l'affiche plus
air_quality = deque(maxlen=30)     # indice 0-100

# ------------------ MQTT ------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connecté au broker, code:", reason_code)
    client.subscribe(CONTROL_TOPIC)

def on_message(client, userdata, msg):
    global current_mode, current_interval, TEMP_ALERT_THRESHOLD
    try:
        data = json.loads(msg.payload.decode())
        print("Commande descendante reçue:", data)

        action = data.get("action")

        if action == "set_mode":
            mode = data.get("mode", "normal")
            if mode not in ["normal", "eco"]:
                print("Mode invalide, valeurs possibles: 'normal' ou 'eco'")
                return
            current_mode = mode
            if current_mode == "normal":
                current_interval = PUBLISH_INTERVAL_NORMAL
            else:
                current_interval = PUBLISH_INTERVAL_ECO
            print(f"Nouveau mode: {current_mode}, intervalle = {current_interval}s")

        elif action == "set_temp_alert":
            try:
                new_threshold = float(data.get("threshold", TEMP_ALERT_THRESHOLD))
                TEMP_ALERT_THRESHOLD = new_threshold
                print(f"Nouveau seuil d'alerte température: {TEMP_ALERT_THRESHOLD} °C")
            except ValueError:
                print("Seuil invalide")

        else:
            print("Action inconnue dans la commande")

    except Exception as e:
        print("Erreur traitement commande:", e)

# Client MQTT (API v2)
client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT)
client.loop_start()

# ------------------ SIMULATION CAPTEUR ------------------
def simulate_weather_payload():
    """
    Génère une mesure météo : température, humidité, pression, qualité de l'air.
    """
    temperature = round(uniform(18.0, 32.0), 2)
    humidity = round(uniform(30.0, 80.0), 2)
    pressure = round(uniform(990.0, 1030.0), 2)
    quality_index = round(uniform(20.0, 90.0), 1)

    payload = {
        "device_id": CLIENT_ID,
        "timestamp": int(time.time()),
        "mode": current_mode,
        "temperature_c": temperature,
        "humidity_percent": humidity,
        "pressure_hpa": pressure,
        "air_quality_index": quality_index,
        "temp_alert_threshold": TEMP_ALERT_THRESHOLD
    }
    return payload

def publish_data():
    payload = simulate_weather_payload()
    client.publish(DATA_TOPIC, json.dumps(payload))
    return payload

# ------------------ DASHBOARD ------------------
def update_dashboard(payload):
    ts_str = time.strftime('%H:%M:%S', time.localtime(payload["timestamp"]))
    timestamps.append(ts_str)
    temperatures.append(payload["temperature_c"])
    humidities.append(payload["humidity_percent"])
    pressures.append(payload["pressure_hpa"])          # gardé pour les données, pas tracé
    air_quality.append(payload["air_quality_index"])

    clear_output(wait=True)

    fig = go.Figure()

    # Température (axe Y gauche)
    fig.add_trace(go.Scatter(
        x=list(timestamps),
        y=list(temperatures),
        mode='lines+markers',
        name='Température (°C)'
    ))

    # Humidité (axe Y droit)
    fig.add_trace(go.Scatter(
        x=list(timestamps),
        y=list(humidities),
        mode='lines+markers',
        name='Humidité (%)',
        yaxis='y2'
    ))

    # Layout avec seulement 2 axes Y
    fig.update_layout(
        title=f"Station météo virtuelle - Mode: {current_mode} (intervalle = {current_interval}s)",
        xaxis=dict(title="Heure"),
        yaxis=dict(title="Température (°C)", side='left'),
        yaxis2=dict(
            title="Humidité (%)",
            overlaying='y',
            side='right'
        ),
        height=600
    )

    # Jauge qualité de l'air
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=air_quality[-1],
        title={'text': "Qualité de l'air (0=bon, 100=mauvais)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "red"}
            ]
        }
    ))

    # Vérifier si alerte température
    alert_msg = ""
    if payload["temperature_c"] >= TEMP_ALERT_THRESHOLD:
        alert_msg = f"ALERTE: température {payload['temperature_c']} °C >= seuil {TEMP_ALERT_THRESHOLD} °C !!!"

    print("Dernière mesure :", payload)
    if alert_msg:
        print(alert_msg)

    display(fig)
    display(gauge)

# ------------------ BOUCLE PRINCIPALE ------------------
print("Simulation de station météo virtuelle démarrée. Ctrl+C pour arrêter.")
try:
    while True:
        data = publish_data()
        update_dashboard(data)
        time.sleep(current_interval)
except KeyboardInterrupt:
    print("Simulation arrêtée par l'utilisateur")
    client.loop_stop()
