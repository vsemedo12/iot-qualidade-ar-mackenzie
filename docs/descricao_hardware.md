# Descrição do Hardware

## Plataforma de Prototipagem

### ESP32 NodeMCU ESP-32S
- Processador: Dual-core Xtensa LX6, 240 MHz
- Memória: 520 KB SRAM, 4 MB Flash
- Conectividade: Wi-Fi 802.11 b/g/n (2,4 GHz), Bluetooth 4.2
- GPIO: 34 pinos programáveis
- ADC: 12 bits (0–4095)
- Interfaces: I2C, SPI, UART
- Alimentação: 5V via USB
- Simulação: https://wokwi.com/projects/465002858456776705

---

## Sensores

### MQ-135 – Sensor de Qualidade do Ar
- Tipo: Analógico
- Gases detectados: CO2, NH3, benzeno, fumaça
- Tensão de operação: 5V
- Saída analógica (AOUT): 0V a 5V
- Saída digital (DOUT): configurável por potenciômetro
- Conexão: GPIO 34 (ADC) do ESP32
- Limiar de acionamento: ADC > 2500 (escala 0–4095)

### DHT22 (AM2302) – Sensor de Temperatura e Umidade
- Tipo: Digital (protocolo single-wire)
- Faixa de temperatura: -40°C a 80°C (±0,5°C)
- Faixa de umidade: 0% a 100% UR (±2%)
- Resolução: 16 bits
- Tensão de operação: 3,3V
- Conexão: GPIO 4 do ESP32
- Pull-up: resistor 10 kΩ entre DATA e VCC

---

## Atuador

### Ventilador Exaustor DC 5V
- Tensão de operação: 5V DC
- Corrente: ~200 mA
- Controle: transistor NPN BC547 acionado pelo GPIO 26
- Lógica: ligado quando Gas ADC > 2500, desligado após 2 ciclos abaixo do limiar

---

## Componentes Auxiliares

### Transistor NPN BC547
- Função: chave eletrônica para controle do ventilador
- VCEO máximo: 45V
- IC máximo: 100 mA
- hFE: 110–800
- Conexão: Base → GPIO 26 via 1 kΩ, Coletor → ventilador, Emissor → GND

### Resistores
- 1 kΩ: limitação de corrente na base do BC547
- 10 kΩ: pull-up no pino DATA do DHT22
- Tipo: filme de carbono, tolerância ±5%, 1/4W

### Protoboard e Jumpers
- Protoboard: 830 pontos
- Jumpers: macho-macho 20 cm

### Fonte de Alimentação
- Tensão: 5V DC
- Corrente máxima: 2A
- Alimenta: ESP32 (via USB) e ventilador

---

## Interfaces e Protocolos de Comunicação

### Wi-Fi
- Padrão: IEEE 802.11 b/g/n (2,4 GHz)
- Módulo: integrado no ESP32 (Espressif WROOM-32)
- Rede simulada: Wokwi-GUEST (Public IoT Gateway)

### MQTT
- Broker: Node-RED local (localhost:1883)
- Biblioteca: paho-mqtt (Python)
- QoS: 0
- Tópicos publicados: mackenzie/ar/qualidade, temperatura, umidade, ventilador
- Tópico subscrito: mackenzie/ar/cmd (FAN_ON / FAN_OFF)

### Dashboard
- Plataforma: Node-RED (http://localhost:1880/ui)
- Pacotes: node-red-dashboard, node-red-contrib-aedes
