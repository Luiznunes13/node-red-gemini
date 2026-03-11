# ESP8266 Firmware - MCP Node-RED GPIO

Firmware para ESP8266 integrado ao ecossistema MCP + Node-RED + MQTT.

## Fluxo completo

```
Gemini CLI → main.py (MCP) → Node-RED → MQTT Broker → ESP8266 → GPIOs
```

## Arquivos

```
esp8266_firmware/
├── esp8266_firmware.ino   # Firmware principal
└── config.h               # Configurações (WiFi, MQTT, Device ID)
```

## Configuração rápida

### 1. Editar config.h

```cpp
#define DEVICE_ID     "esp8266-01"        // ID único por device
#define WIFI_SSID     "SUA_REDE_WIFI"
#define WIFI_PASSWORD "SUA_SENHA_WIFI"
#define MQTT_HOST     "192.168.0.X"       // IP do broker MQTT
#define MQTT_PORT     1883
```

### 2. Instalar bibliotecas no Arduino IDE

| Biblioteca | Versão | Instalar via |
|---|---|---|
| ESP8266 core | >= 3.1 | Board Manager |
| PubSubClient | >= 2.8 | Library Manager |
| ArduinoJson | >= 6.x | Library Manager |

> Board Manager URL: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`

### 3. Compilar e gravar

- Board: **NodeMCU 1.0 (ESP-12E Module)**
- Flash Size: **4MB (FS:2MB OTA:~1019KB)**
- CPU Frequency: **80 MHz**
- Upload Speed: **115200**

---

## Tópicos MQTT

### Subscritos (ESP8266 recebe)

| Tópico | Payload | Descrição |
|---|---|---|
| `mcp/gpio/{pin}/set` | `"1"` / `"0"` / `"on"` / `"off"` | Controla pino individual |
| `mcp/gpio/all/set` | `[{"pin":2,"state":"on"},...]` | Controla múltiplos pinos |
| `mcp/device/{id}/ota` | URL do firmware | Atualização OTA remota |

### Publicados (ESP8266 envia)

| Tópico | Payload | Retain | Descrição |
|---|---|---|---|
| `mcp/gpio/{pin}/status` | `"1"` ou `"0"` | ✅ | Estado atual do pino |
| `mcp/device/{id}/online` | `"1"` / LWT: `"0"` | ✅ | Heartbeat / presença |
| `mcp/device/{id}/info` | JSON | ✅ | IP, RSSI, versão, heap |
| `mcp/device/{id}/rssi` | `-70` | ❌ | Sinal WiFi |

---

## Pinos disponíveis no ESP8266

| Pino BCM | Pino NodeMCU | Observação |
|---|---|---|
| 2  | D4 | LED interno (invertido) |
| 4  | D2 | GPIO livre |
| 5  | D1 | GPIO livre |
| 12 | D6 | GPIO livre |
| 13 | D7 | GPIO livre |
| 14 | D5 | GPIO livre |
| 16 | D0 | Conectado ao RST para deep sleep |

---

## Configurar Node-RED para publicar no MQTT

No flow existente (`mcp_all_gpios.json`), adicione um nó **MQTT out** após a função de controle:

```
[HTTP in] → [function: processa GPIO] → [MQTT out: mcp/gpio/{{pin}}/set]
```

**Configuração do nó MQTT out:**
- Server: IP do broker : 1883
- Topic: `mcp/gpio/` (dinâmico via `msg.topic`)
- QoS: 1
- Retain: false

---

## Instalar broker MQTT (Mosquitto)

```bash
# No servidor / Raspberry Pi / VPS
sudo apt-get install mosquitto mosquitto-clients

# Habilitar e iniciar
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Testar
mosquitto_sub -h localhost -t "mcp/#" -v
```

---

## OTA - Atualização sem fio

Após o firmware estar rodando:

```bash
# Via Arduino IDE:
# Ferramentas → Porta → selecionar "esp8266-01 at 192.168.0.X"
# Sketch → Upload

# Via Python (esptool):
python -m esptool --port /dev/ttyUSB0 write_flash 0x0 firmware.bin
```

---

## Múltiplos devices

Para adicionar mais ESPs, basta alterar o `DEVICE_ID` no `config.h` de cada um:

```cpp
// ESP #1 - Sala
#define DEVICE_ID "esp8266-sala"

// ESP #2 - Garagem  
#define DEVICE_ID "esp8266-garagem"

// ESP #3 - Industrial Máquina A
#define DEVICE_ID "esp8266-maquina-a"
```

Todos recebem os mesmos tópicos `mcp/gpio/+/set` mas apenas respondem ao próprio `mcp/device/{id}/*`.
