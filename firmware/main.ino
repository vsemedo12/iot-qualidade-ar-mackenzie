/*
 * Sistema de Monitoramento da Qualidade do Ar Urbano
 * Universidade Presbiteriana Mackenzie – FCI
 * Autor: Victor Semedo, Willian Costa
 * Plataforma: ESP32 NodeMCU ESP-32S
 * Sensores: MQ-135 (GPIO 34), DHT22 (GPIO 4)
 * Atuador:  Ventilador via BC547 (GPIO 26)
 * Protocolo: MQTT (broker local Node-RED / broker.emqx.io)
 * Simulação: Wokwi – https://wokwi.com/projects/465002858456776705
 */

#include <WiFi.h>
#include <ArduinoMqttClient.h>
#include <DHT.h>

// ── Wi-Fi ────────────────────────────────────────────────────────────────────
const char* WIFI_SSID     = "Wokwi-GUEST";  // para simulação no Wokwi
const char* WIFI_PASSWORD = "";              // sem senha na rede simulada

// ── MQTT ─────────────────────────────────────────────────────────────────────
// Para simulação no Wokwi: usar broker.emqx.io porta 8083 (WebSocket)
// Para hardware real:      usar broker local ou broker.emqx.io porta 1883
const char* MQTT_BROKER = "broker.emqx.io";
const int   MQTT_PORT   = 8083;

// ── Tópicos ──────────────────────────────────────────────────────────────────
const char* TOPIC_QUALIDADE   = "mackenzie/ar/qualidade";
const char* TOPIC_TEMPERATURA = "mackenzie/ar/temperatura";
const char* TOPIC_UMIDADE     = "mackenzie/ar/umidade";
const char* TOPIC_VENTILADOR  = "mackenzie/ar/ventilador";
const char* TOPIC_CMD         = "mackenzie/ar/cmd";

// ── Pinos ────────────────────────────────────────────────────────────────────
#define PIN_MQ135  34   // Saída analógica do sensor MQ-135
#define PIN_DHT     4   // Data do sensor DHT22
#define PIN_FAN    26   // Base do transistor BC547 (ventilador)

// ── Constantes ───────────────────────────────────────────────────────────────
#define DHT_TYPE     DHT22
#define LIMIAR_GAS   2500   // ADC acima deste valor aciona o ventilador
#define INTERVALO_MS 5000   // Ciclo de leitura: 5 segundos

// ── Objetos ──────────────────────────────────────────────────────────────────
DHT        dht(PIN_DHT, DHT_TYPE);
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// ── Estado ───────────────────────────────────────────────────────────────────
bool          fanOn       = false;
int           abaixoCount = 0;
unsigned long lastMs      = 0;

// ═════════════════════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PIN_FAN, OUTPUT);
  digitalWrite(PIN_FAN, LOW);

  dht.begin();
  delay(2000); // DHT22 precisa de 2s para estabilizar

  // Conectar Wi-Fi
  Serial.printf("[WiFi] Conectando a %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n[WiFi] Conectado! IP: %s\n", WiFi.localIP().toString().c_str());

  // Conectar MQTT
  mqttClient.setId("esp32_mackenzie_10341694");
  mqttClient.onMessage(onMqttMessage);

  Serial.printf("[MQTT] Conectando a %s:%d...\n", MQTT_BROKER, MQTT_PORT);
  while (!mqttClient.connect(MQTT_BROKER, MQTT_PORT)) {
    Serial.printf("[MQTT] Falha! Erro: %d. Tentando em 3s...\n", mqttClient.connectError());
    delay(3000);
  }
  Serial.println("[MQTT] Conectado!");

  mqttClient.subscribe(TOPIC_CMD);
  Serial.printf("[MQTT] Inscrito em: %s\n", TOPIC_CMD);
}

// ═════════════════════════════════════════════════════════════════════════════
void loop() {
  mqttClient.poll(); // mantém conexão ativa e processa mensagens recebidas

  unsigned long agora = millis();
  if (agora - lastMs >= INTERVALO_MS) {
    lastMs = agora;

    // ── 1. Leitura dos sensores ──────────────────────────────────────────
    int   adcGas = analogRead(PIN_MQ135);
    float temp   = dht.readTemperature();
    float umid   = dht.readHumidity();

    if (isnan(temp) || isnan(umid)) {
      Serial.println("[ERRO] Falha na leitura do DHT22 — tentando no proximo ciclo");
      return;
    }

    Serial.printf("[SENSOR] Gas ADC: %d | Temp: %.1fC | Umid: %.1f%%\n",
                  adcGas, temp, umid);

    // ── 2. Controle do atuador ──────────────────────────────────────────
    controlarVentilador(adcGas);

    // ── 3. Publicação MQTT ──────────────────────────────────────────────
    unsigned long t0 = millis();

    publicar(TOPIC_QUALIDADE,   String(adcGas));
    publicar(TOPIC_TEMPERATURA, String(temp, 1));
    publicar(TOPIC_UMIDADE,     String(umid, 1));
    publicar(TOPIC_VENTILADOR,  fanOn ? "ON" : "OFF");

    Serial.printf("[MQTT] Publicado em %lu ms\n", millis() - t0);
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Controla o ventilador conforme o nível de gás detectado
// ─────────────────────────────────────────────────────────────────────────────
void controlarVentilador(int adcGas) {
  if (adcGas > LIMIAR_GAS) {
    if (!fanOn) {
      fanOn = true;
      abaixoCount = 0;
      digitalWrite(PIN_FAN, HIGH);
      Serial.println("[ATUADOR] Ventilador LIGADO");
    }
  } else {
    abaixoCount++;
    if (fanOn && abaixoCount >= 2) {
      fanOn = false;
      abaixoCount = 0;
      digitalWrite(PIN_FAN, LOW);
      Serial.println("[ATUADOR] Ventilador DESLIGADO");
    }
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Publica uma mensagem em um tópico MQTT
// ─────────────────────────────────────────────────────────────────────────────
void publicar(const char* topic, String valor) {
  mqttClient.beginMessage(topic);
  mqttClient.print(valor);
  mqttClient.endMessage();
  Serial.printf("[MQTT] %s -> %s\n", topic, valor.c_str());
}

// ═════════════════════════════════════════════════════════════════════════════
// Callback: processa comandos recebidos via MQTT
// ─────────────────────────────────────────────────────────────────────────────
void onMqttMessage(int messageSize) {
  String topic = mqttClient.messageTopic();
  String msg   = "";
  while (mqttClient.available()) msg += (char)mqttClient.read();
  msg.trim();
  msg.toUpperCase();

  Serial.printf("[CMD] %s -> %s\n", topic.c_str(), msg.c_str());

  if (topic == TOPIC_CMD) {
    if (msg == "FAN_ON") {
      fanOn = true;
      digitalWrite(PIN_FAN, HIGH);
      publicar(TOPIC_VENTILADOR, "ON");
      Serial.println("[CMD] Ventilador LIGADO remotamente");
    } else if (msg == "FAN_OFF") {
      fanOn = false;
      digitalWrite(PIN_FAN, LOW);
      publicar(TOPIC_VENTILADOR, "OFF");
      Serial.println("[CMD] Ventilador DESLIGADO remotamente");
    }
  }
}
