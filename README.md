# 🌿 Sistema Inteligente de Monitoramento da Qualidade do Ar Urbano com IoT e ESP32

**Universidade Presbiteriana Mackenzie — Faculdade de Computação e Informática**  
**Disciplina:** Objetos Inteligentes Conectados  
**Autores:** Victor Semedo
**Ano:** 2026

---

## 📋 Descrição do Projeto

Sistema de monitoramento da qualidade do ar em ambientes urbanos utilizando tecnologias de Internet das Coisas (IoT), alinhado ao **Objetivo de Desenvolvimento Sustentável 11 (ODS 11)** — Cidades e Comunidades Sustentáveis, meta 11.6.

O sistema coleta dados ambientais em tempo real por meio de sensores conectados a um microcontrolador ESP32, publica os dados via protocolo **MQTT** a um broker remoto e aciona automaticamente um ventilador exaustor quando os níveis de poluentes ultrapassam limiares críticos.

---

## ⚙️ Hardware Utilizado

| Componente | Especificação | Conexão |
|---|---|---|
| Microcontrolador | ESP32 NodeMCU ESP-32S | — |
| Sensor de gás | MQ-135 (CO2, NH3, benzeno, fumaça) | GPIO 34 (ADC) |
| Sensor temp/umidade | DHT22 (AM2302) | GPIO 4 |
| Atuador | Ventilador exaustor DC 5V | GPIO 26 (via BC547) |
| Transistor | NPN BC547 | Base → GPIO 26 via 1kΩ |
| Resistores | 1kΩ (base BC547), 10kΩ (pull-up DHT22) | — |
| Protoboard | 830 pontos | — |
| Fonte | 5V / 2A | ESP32 + Ventilador |

### Diagrama de Conexões

```
MQ-135:  VCC → 3.3V | GND → GND | AOUT → GPIO34
DHT22:   VCC → 3.3V | GND → GND | DATA → GPIO4 (+ pull-up 10kΩ)
BC547:   Base → GPIO26 via 1kΩ | Coletor → Ventilador+ | Emissor → GND
```

---

## 🖥️ Software Desenvolvido

### Plataforma de Simulação
- **Wokwi** — simulação do circuito ESP32 online

### Firmware (Arduino IDE v2.x)
- Linguagem: C++ (Arduino Framework)
- Bibliotecas:
  - `WiFi.h` — conectividade Wi-Fi do ESP32
  - `PubSubClient` — cliente MQTT
  - `DHT sensor library` — leitura do sensor DHT22

### Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────┐
│                   LOOP PRINCIPAL (5s)               │
│                                                     │
│  1. Leitura MQ-135 (ADC 12 bits, 0–4095)           │
│  2. Leitura DHT22 (temperatura + umidade)           │
│  3. Comparação com limiar (ADC > 2500?)             │
│     ├── SIM → Ventilador ON (GPIO26 HIGH)           │
│     └── NÃO → Ventilador OFF (GPIO26 LOW)           │
│  4. Publicação MQTT nos tópicos:                    │
│     ├── mackenzie/ar/qualidade                      │
│     ├── mackenzie/ar/temperatura                    │
│     ├── mackenzie/ar/umidade                        │
│     └── mackenzie/ar/ventilador                     │
└─────────────────────────────────────────────────────┘
```

---

## 📡 Interfaces, Protocolos e Módulos de Comunicação

| Item | Detalhe |
|---|---|
| Protocolo | MQTT (Message Queuing Telemetry Transport) |
| Broker | `broker.emqx.io` — porta `1883` |
| Modelo | Publish/Subscribe |
| Cliente de monitoramento | MQTTX (desktop) |
| Conectividade | Wi-Fi 802.11 b/g/n (integrado ao ESP32) |
| Biblioteca MQTT | PubSubClient |

### Tópicos MQTT

| Tópico | Conteúdo | Tipo |
|---|---|---|
| `mackenzie/ar/qualidade` | Leitura ADC do MQ-135 (0–4095) | Publisher |
| `mackenzie/ar/temperatura` | Temperatura em °C | Publisher |
| `mackenzie/ar/umidade` | Umidade relativa em % | Publisher |
| `mackenzie/ar/ventilador` | Estado do atuador: ON / OFF | Publisher |
| `mackenzie/ar/cmd` | Comando remoto para o ventilador | Subscriber |

---

## 🚀 Como Reproduzir

### Pré-requisitos
- Conta no [Wokwi](https://wokwi.com) (gratuita)
- [MQTTX](https://mqttx.app) instalado (gratuito)
- Arduino IDE v2.x com ESP32 Board Manager

### Passo a Passo

1. **Clone este repositório**
   ```bash
   git clone https://github.com/vsemedo/iot-qualidade-ar-mackenzie.git
   ```

2. **Abra no Wokwi**
   - Acesse [wokwi.com](https://wokwi.com)
   - Crie um novo projeto ESP32
   - Importe o arquivo `diagram.json`
   - Cole o conteúdo de `sketch.ino` no editor

3. **Execute a simulação**
   - Clique em ▶ para iniciar
   - Gire o potenciômetro (MQ-135) para simular variação de gás
   - Observe o Serial Monitor

4. **Monitore via MQTTX**
   - Abra o MQTTX
   - Nova conexão: `broker.emqx.io` porta `1883`
   - Subscribe em `mackenzie/#`
   - Veja os dados chegando em tempo real

---

## 📁 Estrutura do Repositório

```
iot-qualidade-ar-mackenzie/
├── sketch.ino          # Firmware do ESP32
├── diagram.json        # Diagrama do circuito (Wokwi)
├── libraries.txt       # Bibliotecas utilizadas
└── README.md           # Este arquivo
```

---

## 🔗 Links

- 📄 [Artigo completo (PDF)](./Projeto_IoT_2026_ODS11.pdf) *(adicionar após entrega)*
- 🎥 [Vídeo demonstração (YouTube)](https://youtube.com) *(adicionar após gravação)*
- 🌐 [ODS 11 — ONU](https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustentavel)

---

## 📚 Referências

- KUMAR, N. M.; LIM, F. K. MQTT protocol for IoT-based environmental monitoring systems: a review. *Procedia Computer Science*, v. 159, p. 742–749, 2019.
- SANTOS, B. et al. *Internet das Coisas: da teoria à prática*. Belo Horizonte: UFMG, 2019.
- OMS. *Ambient (outdoor) air pollution*. Geneva: WHO, 2022.
- ONU. *Agenda 2030 para o Desenvolvimento Sustentável*. Nova York: ONU, 2015.
