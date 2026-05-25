"""
Simulador ESP32 – Sistema de Monitoramento da Qualidade do Ar Urbano
Universidade Presbiteriana Mackenzie – FCI
Autor: Victor Semedo, Willian Costa
Protocolo: MQTT via broker.emqx.io (TCP/IP – internet real)
"""

import paho.mqtt.client as mqtt
import random
import time

# ── Configurações MQTT ────────────────────────────────────────────────────────
BROKER    = "broker.emqx.io"
PORT      = 1883
CLIENT_ID = "esp32_mac_vs_wc_2026_xyz987"

TOPIC_QUALIDADE   = "mackenzie/ar/qualidade"
TOPIC_TEMPERATURA = "mackenzie/ar/temperatura"
TOPIC_UMIDADE     = "mackenzie/ar/umidade"
TOPIC_VENTILADOR  = "mackenzie/ar/ventilador"
TOPIC_CMD         = "mackenzie/ar/cmd"

# ── Estado ───────────────────────────────────────────────────────────────────
fan_on        = False
abaixo_count  = 0
LIMIAR_GAS    = 2500

# Controle de latência
publish_times = {}
latencias     = []

# ── Callbacks ────────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[MQTT] Conectado ao broker externo {BROKER}!")
        client.subscribe(TOPIC_CMD)
    else:
        print(f"[MQTT] Falha! rc={rc}")

def on_publish(client, userdata, mid, *args):
    t1 = time.time()
    if mid in publish_times:
        lat = round((t1 - publish_times[mid]) * 1000, 1)
        latencias.append(lat)
        publish_times.pop(mid)

def on_message(client, userdata, msg):
    global fan_on
    comando = msg.payload.decode().strip().upper()
    print(f"[CMD] {msg.topic} -> {comando}")
    if comando == "FAN_ON":
        fan_on = True
        client.publish(TOPIC_VENTILADOR, "ON")
    elif comando == "FAN_OFF":
        fan_on = False
        client.publish(TOPIC_VENTILADOR, "OFF")

def controlar_ventilador(client, adc_gas):
    global fan_on, abaixo_count
    if adc_gas > LIMIAR_GAS:
        if not fan_on:
            fan_on = True
            abaixo_count = 0
            t0 = time.time()
            info = client.publish(TOPIC_VENTILADOR, "ON")
            publish_times[info.mid] = t0
            print("[ATUADOR] Ventilador LIGADO (gas alto!)")
    else:
        abaixo_count += 1
        if fan_on and abaixo_count >= 2:
            fan_on = False
            abaixo_count = 0
            t0 = time.time()
            info = client.publish(TOPIC_VENTILADOR, "OFF")
            publish_times[info.mid] = t0
            print("[ATUADOR] Ventilador DESLIGADO")

def publicar(client, topic, valor):
    t0 = time.time()
    info = client.publish(topic, str(valor))
    publish_times[info.mid] = t0
    return info

def gerar_gas():
    """
    Gera leitura de gás de forma aleatória e realista:
    - 70% do tempo: ar normal (800–2200 ADC)
    - 30% do tempo: poluição elevada (2600–3800 ADC)
    Simula variações reais de qualidade do ar urbano.
    """
    if random.random() < 0.30:
        return random.randint(2600, 3800)  # poluição elevada
    else:
        return random.randint(800, 2200)   # ar normal

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish  = on_publish

    print(f"[WiFi] Conectando via internet a {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    time.sleep(3)

    ciclo = 0
    print("\n[SIM] Iniciando ciclos de leitura (5s cada)...\n")
    print(f"{'Ciclo':<6} {'Gas ADC':<10} {'Temp(C)':<10} {'Umid(%)':<10} {'Latencia(ms)':<15} {'Ventilador'}")
    print("-" * 65)

    while True:
        ciclo += 1

        # Geração aleatória e realista dos sensores
        adc_gas     = gerar_gas()
        temperatura = round(random.uniform(24.0, 32.0), 1)
        umidade     = round(random.uniform(55.0, 80.0), 1)

        controlar_ventilador(client, adc_gas)

        publicar(client, TOPIC_QUALIDADE,   adc_gas)
        publicar(client, TOPIC_TEMPERATURA, temperatura)
        publicar(client, TOPIC_UMIDADE,     umidade)

        time.sleep(0.5)

        lat = latencias[-1] if latencias else 0
        print(f"{ciclo:<6} {adc_gas:<10} {temperatura:<10} {umidade:<10} {lat:<15} {'ON' if fan_on else 'OFF'}")

        if ciclo % 4 == 0 and latencias:
            media = round(sum(latencias[-12:]) / len(latencias[-12:]), 1)
            print(f"\n  >> Latencia media MQTT (ultimas medicoes): {media} ms\n")

        time.sleep(4.5)

if __name__ == "__main__":
    main()
