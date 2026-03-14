# 🤖 Node-RED Gemini MCP — Automação IoT com ESP8266

> Servidor MCP (Model Context Protocol) que integra o **Gemini CLI** ao **Node-RED**, permitindo controlar GPIOs, ler sensores DHT11 e criar automações autônomas no ESP8266 usando linguagem natural.

---

## 🏗️ Arquitetura do Sistema

```
Gemini CLI → main.py (MCP) → Node-RED (HTTP REST) → MQTT (Mosquitto) → ESP8266 → GPIO / DHT11
```

```
┌─────────────┐    MCP/stdio    ┌──────────────┐    HTTP REST    ┌─────────────┐
│  Gemini CLI │ ──────────────▶ │   main.py    │ ──────────────▶ │  Node-RED   │
│  (IA)       │                 │  (Servidor   │                 │  (Flow      │
└─────────────┘                 │   MCP)       │                 │   Engine)   │
                                └──────────────┘                 └──────┬──────┘
                                                                         │ MQTT
                                                                         ▼
                                                                  ┌─────────────┐
                                                                  │  Mosquitto  │
                                                                  │  (Broker)   │
                                                                  └──────┬──────┘
                                                                         │ MQTT
                                                                         ▼
                                                                  ┌─────────────┐
                                                                  │   ESP8266   │
                                                                  │  NodeMCU    │
                                                                  │             │
                                                                  │  D2 → DHT11 │
                                                                  │  D5 → LED   │
                                                                  └─────────────┘
```

---

## 📦 Pré-requisitos

| Componente | Versão mínima | Observação |
|---|---|---|
| Python | 3.8+ (testado com 3.13) | Para executar o servidor MCP |
| Node-RED | 4.0+ | Orquestrador de flows |
| Mosquitto | 2.0+ | Broker MQTT |
| Arduino IDE | 1.8+ | Para gravar firmware no ESP8266 |
| ESP8266 core | >= 3.1 | Board Manager do Arduino IDE |
| Gemini CLI | última versão | Interface de IA |

---

## 🔌 Mapeamento de Hardware

| Dispositivo | Pino GPIO | Pino NodeMCU | Tipo | Descrição |
|---|---|---|---|---|
| LED principal | GPIO 14 | D5 | Saída | LED controlável |
| Sensor DHT11 | GPIO 4 | D2 | Entrada | Temperatura e umidade |

---

## 📁 Estrutura do Projeto

```
node-red-gemini/
├── main.py                    # Servidor MCP principal (12 ferramentas)
├── mcp_mqtt_esp8266.json      # Flow Node-RED completo com MQTT + DHT11
├── mcp-config.json            # Configuração do Gemini CLI
├── requirements.txt           # Dependências Python (mcp>=1.19.0, httpx>=0.27.0)
├── GEMINI.md                  # Contexto e instruções para o Gemini CLI
├── .gitignore
├── esp8266_firmware/
│   ├── esp8266_firmware.ino   # Firmware principal
│   ├── config.h.example       # Template de configuração (WiFi, MQTT)
│   └── README.md              # Documentação do firmware
└── README.md
```

---

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Luiznunes13/node-red-gemini.git
cd node-red-gemini
```

### 2. Instalar dependências Python

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou: .venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Instalar e configurar o Mosquitto (MQTT Broker)

```bash
# Ubuntu/Debian
sudo apt-get install mosquitto mosquitto-clients

# Habilitar e iniciar
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Testar
mosquitto_sub -h localhost -t "mcp/#" -v
```

### 4. Instalar e configurar o Node-RED

```bash
# Instalar Node-RED globalmente
npm install -g --unsafe-perm node-red

# Iniciar Node-RED
node-red
```

Após iniciar, acesse `http://localhost:1880` e importe o flow:

1. Menu (≡) → **Import** → **select a file to import**
2. Selecione o arquivo `mcp_mqtt_esp8266.json`
3. Clique em **Deploy** 🟢

### 5. Configurar o firmware ESP8266

```bash
# Copiar o template de configuração
cp esp8266_firmware/config.h.example esp8266_firmware/config.h
```

Edite `esp8266_firmware/config.h` com suas credenciais:

```cpp
#define DEVICE_ID     "esp8266-01"        // ID único por device
#define WIFI_SSID     "SUA_REDE_WIFI"
#define WIFI_PASSWORD "SUA_SENHA_WIFI"
#define MQTT_HOST     "192.168.0.X"       // IP do broker Mosquitto
#define MQTT_PORT     1883
```

Instale as bibliotecas no Arduino IDE (via Library Manager):

| Biblioteca | Versão |
|---|---|
| PubSubClient | >= 2.8 |
| ArduinoJson | >= 6.x |
| DHT sensor library | >= 1.4 |

> Board Manager URL: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`

Configurações de upload:
- **Board:** NodeMCU 1.0 (ESP-12E Module)
- **Flash Size:** 4MB (FS:2MB OTA:~1019KB)
- **CPU Frequency:** 80 MHz
- **Upload Speed:** 115200

### 6. Configurar o Gemini CLI

O arquivo `mcp-config.json` já está configurado para conectar ao servidor MCP (`main.py`).
O arquivo `GEMINI.md` contém o contexto e as instruções que o Gemini usa para entender o projeto.

```bash
# Iniciar o Gemini CLI apontando para esta pasta
gemini
```

---

## 🛠️ Ferramentas MCP Disponíveis (12 no total)

### 🔌 GPIO — Controle de Pinos

| Ferramenta | Descrição |
|---|---|
| `control_gpio_mcp` | Controla o estado de um pino GPIO individual (`on`/`off`) |
| `control_multiple_gpio_mcp` | Controla múltiplos pinos GPIO em uma única chamada |
| `get_gpio_status_mcp` | Retorna o estado atual de um pino GPIO |
| `list_mcp_tools` | Lista todas as ferramentas disponíveis no Node-RED |
| `deploy_mcp_gpio_flow` | Faz deploy de um novo flow GPIO no Node-RED |

### 🌡️ Sensor DHT11 — Temperatura e Umidade

| Ferramenta | Descrição |
|---|---|
| `get_dht_sensor_mcp` | Lê temperatura e umidade atuais do sensor DHT11 (pino D2/GPIO 4) |
| `set_sensor_alert` | Configura um limiar de alerta (ex: avisar se temperatura > 28°C) |
| `get_sensor_alerts` | Consulta os alertas que foram disparados |
| `clear_sensor_alerts` | Limpa a fila de alertas |

### 🤖 Automação Autônoma — Planos de Ação

| Ferramenta | Descrição |
|---|---|
| `set_action_plan` | Cria uma regra autônoma executada pelo Node-RED a cada ~30s |
| `list_action_plans` | Lista todos os planos de automação ativos |
| `delete_action_plan` | Remove um plano de automação pelo ID |

#### Triggers disponíveis para `set_action_plan`:

| Trigger | Descrição |
|---|---|
| `temp_above` | Dispara quando temperatura sobe acima do limiar |
| `temp_below` | Dispara quando temperatura cai abaixo do limiar |
| `humidity_above` | Dispara quando umidade sobe acima do limiar |
| `humidity_below` | Dispara quando umidade cai abaixo do limiar |

---

## 💬 Exemplos de Uso por Linguagem Natural

### Controle de LED

| Comando | Ação executada |
|---|---|
| "ligue o led" | `control_gpio_mcp(pin=14, state="on")` |
| "apague o led" | `control_gpio_mcp(pin=14, state="off")` |
| "apague a luz" | `control_gpio_mcp(pin=14, state="off")` |

### Leitura de Sensor

| Comando | Ação executada |
|---|---|
| "qual a temperatura?" | `get_dht_sensor_mcp()` |
| "qual a umidade?" | `get_dht_sensor_mcp()` |
| "leia o sensor" | `get_dht_sensor_mcp()` |
| "como está o clima?" | `get_dht_sensor_mcp()` |

### Alertas Pontuais (requerem Gemini ativo)

| Comando | Ação executada |
|---|---|
| "me avise se a temp > 28°C" | `set_sensor_alert(temp_above=28)` |
| "alerte se a umidade cair abaixo de 40%" | `set_sensor_alert(humidity_below=40)` |
| "tem algum alerta?" | `get_sensor_alerts()` |
| "limpe os alertas" | `clear_sensor_alerts()` |

### Automações Autônomas (Node-RED executa sozinho, sem Gemini)

| Comando | Ação executada |
|---|---|
| "se temperatura passar de 28°C, ligue o led automaticamente" | `set_action_plan(trigger="temp_above", threshold=28, pin=14, action="on", description="ligar led quando ambiente esquentar")` |
| "se temperatura baixar de 24°C, apague o led" | `set_action_plan(trigger="temp_below", threshold=24, pin=14, action="off", description="apagar led quando ambiente esfriar")` |
| "quais automações estão ativas?" | `list_action_plans()` |
| "cancele a regra do led" | `list_action_plans()` → identificar ID → `delete_action_plan(id=...)` |

---

## 📡 Tópicos MQTT

### Subscritos pelo ESP8266 (recebe comandos)

| Tópico | Payload | Descrição |
|---|---|---|
| `mcp/gpio/{pin}/set` | `"1"` / `"0"` / `"on"` / `"off"` | Controla pino individual |
| `mcp/gpio/all/set` | `[{"pin":14,"state":"on"},...]` | Controla múltiplos pinos |
| `mcp/device/{id}/ota` | URL do firmware | Atualização OTA remota |

### Publicados pelo ESP8266 (envia status)

| Tópico | Payload | Retain | Descrição |
|---|---|---|---|
| `mcp/gpio/{pin}/status` | `"1"` ou `"0"` | ✅ | Estado atual do pino |
| `mcp/device/{id}/online` | `"1"` / LWT: `"0"` | ✅ | Heartbeat / presença |
| `mcp/device/{id}/info` | JSON | ✅ | IP, RSSI, versão, heap |
| `mcp/device/{id}/rssi` | `-70` | ❌ | Intensidade do sinal WiFi |

---

## 🔄 Fluxo de Automação Autônoma

O Node-RED executa os planos de ação automaticamente a cada leitura do DHT11 (~30 segundos), **sem necessidade do Gemini estar ativo**. Esta é a forma mais robusta para automação contínua.

```
DHT11 (a cada 30s)
      │
      ▼
Node-RED verifica planos de ação
      │
      ├─ temp > 28°C? → ligar LED (GPIO 14)
      ├─ temp < 24°C? → apagar LED (GPIO 14)
      └─ umidade < 40%? → ativar ventilador (GPIO X)
```

### Fluxo de criação de plano:

```
1. set_action_plan(trigger, threshold, pin, action, description)
   └─ Node-RED passa a executar automaticamente

2. list_action_plans()
   └─ verificar planos ativos

3. get_sensor_alerts()
   └─ ver histórico de execuções automáticas

4. delete_action_plan(id)
   └─ remover uma regra
```

---

## 🔧 Troubleshooting

### Node-RED não responde
```bash
# Verificar se está rodando
curl http://localhost:1880/flows

# Reiniciar
node-red-stop && node-red-start
```

### MQTT sem conexão
```bash
# Verificar status do Mosquitto
sudo systemctl status mosquitto

# Testar publicação
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test" -v
```

### ESP8266 não conecta ao MQTT
- Verifique se o IP do broker em `config.h` está correto
- Confirme que o ESP8266 e o broker estão na mesma rede
- Abra o Serial Monitor (115200 baud) para ver logs de conexão

### Sensor DHT11 retorna valores inválidos
- Verifique a conexão do sensor no pino D2 (GPIO 4)
- O DHT11 precisa de resistor pull-up de 4.7kΩ entre VCC e DATA
- Aguarde pelo menos 2 segundos entre leituras

### Gemini CLI não encontra ferramentas MCP
```bash
# Verificar se o servidor MCP inicia corretamente
python main.py

# Confirmar que mcp-config.json está configurado corretamente
cat mcp-config.json
```

---

## 📊 Status do Projeto

| Item | Valor |
|---|---|
| Versão | 2.0.0 |
| Data | Março 2026 |
| Python | 3.8+ (testado com 3.13) |
| Node-RED | 4.0+ |
| MCP SDK | >= 1.19.0 |
| Ferramentas MCP | 12 |
| Hardware | ESP8266 NodeMCU |

---

## 📄 Licença

MIT License — veja o arquivo `LICENSE` para detalhes.
