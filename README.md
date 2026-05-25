# Sistema Inteligente de Monitoramento da Qualidade do Ar Urbano com IoT e ESP32

**Universidade Presbiteriana Mackenzie – Faculdade de Computação e Informática**  
**Autor:** Victor Semedo  
**Disciplina:** Internet das Coisas (IoT)  
**ODS 11** – Cidades e Comunidades Sustentáveis

---

## Descrição do Projeto

Sistema IoT de baixo custo para monitoramento contínuo da qualidade do ar em ambientes urbanos. O projeto utiliza um script Python para simular o firmware do ESP32, coletando dados dos sensores MQ-135 (gases nocivos) e DHT22 (temperatura/umidade), acionando automaticamente um ventilador exaustor quando os níveis de poluentes ultrapassam o limiar configurado (ADC > 2500), e publicando todos os dados via protocolo MQTT em um broker local gerenciado pelo Node-RED, onde são visualizados em um dashboard em tempo real.

O circuito do ESP32 foi modelado e simulado na plataforma Wokwi (wokwi.com/projects/465002858456776705).

---

## Arquitetura do Sistema

```
[Script Python / ESP32]
        |
        | MQTT (TCP/IP – localhost:1883)
        v
[Broker MQTT – Node-RED local]
        |
        |-- [Dashboard Node-RED] → http://localhost:1880/ui
        |-- [MQTT Explorer]      → visualização dos tópicos
```

---

## Como Reproduzir

### Pré-requisitos
- Python 3.x instalado
- Node.js instalado
- Node-RED instalado (`npm install -g node-red`)
- Pacotes Node-RED: `node-red-contrib-aedes`, `node-red-dashboard`
- Biblioteca Python: `paho-mqtt` (`pip install paho-mqtt`)

### Passo 1 — Iniciar o Node-RED
```bash
node-red
```
Acesse: `http://localhost:1880` e importe o fluxo `node-red/flow.json`.

### Passo 2 — Rodar o script de simulação
```bash
python firmware/esp32_local.py
```
O script publica dados nos tópicos MQTT a cada 5 segundos.

### Passo 3 — Visualizar o dashboard
Acesse: `http://localhost:1880/ui`

### Passo 4 — Monitorar os tópicos MQTT
Abra o MQTT Explorer, conecte em `localhost:1883` e filtre por `mackenzie/#`.

---

## Circuito Virtual (Wokwi)

Acesse a simulação: **https://wokwi.com/projects/465002858456776705**

| Componente | Especificação | GPIO |
|---|---|---|
| ESP32 NodeMCU ESP-32S | Dual-core 240 MHz, Wi-Fi integrado | — |
| Sensor MQ-135 (potenciômetro simulado) | Qualidade do ar, saída analógica | GPIO 34 |
| Sensor DHT22 | Temperatura (-40–80°C) e umidade | GPIO 4 |
| Ventilador (LED azul simulado) | DC 5V, ~200 mA (atuador) | GPIO 26 (via BC547) |
| Transistor BC547 | NPN, chave eletrônica | — |
| Resistor 1 kΩ | Base do BC547 | — |
| Resistor 10 kΩ | Pull-up DHT22 | — |

---

## Tópicos MQTT

| Tópico | Conteúdo | Direção |
|---|---|---|
| `mackenzie/ar/qualidade` | Valor ADC do MQ-135 (0–4095) | Publicação |
| `mackenzie/ar/temperatura` | Temperatura em °C | Publicação |
| `mackenzie/ar/umidade` | Umidade relativa em % | Publicação |
| `mackenzie/ar/ventilador` | Estado do atuador: ON ou OFF | Publicação |
| `mackenzie/ar/cmd` | `FAN_ON` ou `FAN_OFF` (controle remoto) | Subscrição |

---

## Lógica de Acionamento do Atuador

```python
SE leitura_ADC_MQ135 > 2500 ENTÃO
    ligar ventilador (GPIO 26 = HIGH)
    publicar mackenzie/ar/ventilador = "ON"
SENÃO SE ciclos_abaixo >= 2 ENTÃO
    desligar ventilador (GPIO 26 = LOW)
    publicar mackenzie/ar/ventilador = "OFF"
```

---

## Estrutura do Repositório

```
├── firmware/
│   ├── main.ino              # Código ESP32 (Arduino IDE)
│   ├── esp32_local.py        # Script Python – simulação com broker local
│   └── esp32_medicao.py      # Script Python – medição de latência MQTT
├── node-red/
│   └── flow.json             # Fluxo Node-RED (broker + dashboard)
├── wokwi/
│   └── diagram.json          # Diagrama do circuito para Wokwi
├── docs/
│   ├── diagrama_circuito.png # Diagrama esquemático de montagem
│   ├── fluxograma.png        # Fluxograma do firmware
│   └── artigo.pdf            # Artigo científico completo
└── README.md
```

---

## Nota sobre o Wokwi

Durante o desenvolvimento, tentou-se utilizar o simulador Wokwi para executar o firmware ESP32 com comunicação MQTT direta. Identificou-se que o plano gratuito da plataforma bloqueia conexões TCP externas (porta 1883), impossibilitando a comunicação com brokers MQTT remotos. Como solução, o firmware foi adaptado e executado via script Python, simulando o comportamento do ESP32 com publicação dos dados via protocolo MQTT em um broker local gerenciado pelo Node-RED. O circuito permanece disponível no Wokwi para visualização da montagem.

---

## Resultados

- Latência média de publicação MQTT: **0,2 ms** (broker local)
- Ventilador acionado automaticamente quando Gas ADC > 2500
- Dashboard atualizado em tempo real a cada 5 segundos
- Controle remoto do ventilador via tópico `mackenzie/ar/cmd`

---

## Licença

MIT License – livre para uso educacional e reprodução.
