"""
Simulador ESP32 – Sistema de Monitoramento da Qualidade do Ar Urbano
Universidade Presbiteriana Mackenzie – FCI
Autor: Victor Semedo
Protocolo: MQTT via broker local Node-RED (localhost:1883)
"""

import paho.mqtt.client as mqtt
import random
import time

# ── Configurações MQTT ────────────────────────────────────────────────────────
BROKER    = "localhost"
PORT      = 1883
CLIENT_ID = "esp32_mackenzie_10341694"

TOPIC_QUALIDADE   = "mackenzie/ar/qualidade"
TOPIC_TEMPERATURA = "mackenzie/ar/temperatura"
TOPIC_UMIDADE     = "mackenzie/ar/umidade"
TOPIC_VENTILADOR  = "mackenzie/ar/ventilador"
TOPIC_CMD         = "mackenzie/ar/cmd"

# ── Estado ───────────────────────────────────────────────────────────────────
fan_on       = False
abaixo_count = 0
LIMIAR_GAS   = 2500

# ── Callbacks ────────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[MQTT] Conectado ao broker {BROKER}!")
        client.subscribe(TOPIC_CMD)
        print(f"[MQTT] Inscrito em: {TOPIC_CMD}")
    else:
        print(f"[MQTT] Falha na conexao. Codigo: {rc}")

def on_message(client, userdata, msg):
    global fan_on
    comando = msg.payload.decode().strip().upper()
    print(f"[CMD] Topico: {msg.topic} | Mensagem: {comando}")
    if comando == "FAN_ON":
        fan_on = True
        client.publish(TOPIC_VENTILADOR, "ON")
        print("[CMD] Ventilador LIGADO remotamente")
    elif comando == "FAN_OFF":
        fan_on = False
        client.publish(TOPIC_VENTILADOR, "OFF")
        print("[CMD] Ventilador DESLIGADO remotamente")

def on_publish(client, userdata, mid, *args):
    print(f"[MQTT] Mensagem publicada (id={mid})")

def controlar_ventilador(client, adc_gas):
    global fan_on, abaixo_count
    if adc_gas > LIMIAR_GAS:
        if not fan_on:
            fan_on = True
            abaixo_count = 0
            client.publish(TOPIC_VENTILADOR, "ON")
            print("[ATUADOR] Ventilador LIGADO (gas alto!)")
    else:
        abaixo_count += 1
        if fan_on and abaixo_count >= 2:
            fan_on = False
            abaixo_count = 0
            client.publish(TOPIC_VENTILADOR, "OFF")
            print("[ATUADOR] Ventilador DESLIGADO")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish  = on_publish

    print(f"[WiFi] Conectando via internet a {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    time.sleep(2)

    ciclo = 0
    print("\n[SIM] Iniciando ciclos de leitura a cada 5 segundos...\n")

    while True:
        ciclo += 1

        if ciclo in [4, 5]:
            adc_gas = random.randint(2600, 3500)
        else:
            adc_gas = random.randint(800, 2200)

        temperatura = round(random.uniform(24.0, 32.0), 1)
        umidade     = round(random.uniform(55.0, 80.0), 1)

        print(f"[SENSOR] Ciclo {ciclo:02d} | Gas ADC: {adc_gas} | Temp: {temperatura}C | Umid: {umidade}%")

        controlar_ventilador(client, adc_gas)

        t0 = time.time()
        client.publish(TOPIC_QUALIDADE,   str(adc_gas))
        client.publish(TOPIC_TEMPERATURA, str(temperatura))
        client.publish(TOPIC_UMIDADE,     str(umidade))
        latencia = round((time.time() - t0) * 1000)

        print(f"[MQTT]  Publicado em {latencia} ms | Ventilador: {'ON' if fan_on else 'OFF'}\n")

        time.sleep(5)

if __name__ == "__main__":
    main()
