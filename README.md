# 🚀 Servidor MCP para Node-RED + GPIO

Servidor Model Context Protocol (MCP) para automação e controle avançado do Node-RED via linguagem natural, com **controle completo de GPIO** do Raspberry Pi e **API MCP padronizada**.

## ⭐ Funcionalidades Principais

### 🔧 **13 Ferramentas MCP Otimizadas:**

#### 🎛️ **Node-RED Core (8 ferramentas):**
| # | Ferramenta | Descrição |
|---|------------|-----------|
| 1 | `create_node_red_flow` | Cria novos flows personalizados no Node-RED |
| 2 | `get_node_red_flow` | Obtém informações de flow específico |
| 3 | `update_node_red_flow` | Atualiza flows existentes |
| 4 | `delete_node_red_flow` | Remove flows do Node-RED |
| 5 | `deploy_node_red_flows` | Deploy automático de todos os flows |
| 6 | `get_node_red_nodes` | Lista tipos de nós disponíveis |
| 7 | `export_node_red_flow` | Exporta flow para arquivo JSON |
| 8 | `import_node_red_flow` | Importa flow de arquivo JSON |

#### ⚡ **MCP GPIO (5 ferramentas):**
| # | Ferramenta | Descrição |
|---|------------|-----------|
| 1 | `control_gpio_mcp` | 🎯 Controle individual de GPIO (pinos 2-27) |
| 2 | `control_multiple_gpio_mcp` | 🔥 Controle simultâneo de múltiplas GPIOs |
| 3 | `get_gpio_status_mcp` | 📊 Status completo de todas as GPIOs |
| 4 | `list_mcp_tools` | 📋 Lista ferramentas MCP disponíveis |
| 5 | `deploy_mcp_gpio_flow` | 🚀 Deploy de flow MCP GPIO completo |

### 🎯 **Casos de Uso Avançados:**

- 🏠 **Automação Residencial** - Controle por voz/texto de **todas as GPIOs**
- 🤖 **IoT Avançado** - Controle simultâneo de múltiplos dispositivos
- 🎛️ **Dashboard Visual** - Interface Node-RED com API MCP
- 🧠 **Integração IA** - Gemini/Claude CLI com linguagem natural
- ⚡ **Prototipagem Ultra-Rápida** - Deploy automático de flows completos
- 🔌 **Controle Industrial** - GPIO 2-27 com validação e status
- 🌐 **API RESTful** - Endpoints MCP padronizados (`/mcp/gpio/control`, `/mcp/tools`)

### 🆕 **Novidades v2.0:**

- 🔥 **API MCP GPIO Completa** - Controle de **todos os pinos GPIO** (2-27)
- ⚡ **Controle Múltiplo** - Múltiplas GPIOs simultaneamente
- 📊 **Status Global** - Monitoramento centralizado de GPIOs
- 🛡️ **Validação Robusta** - Estados múltiplos (on/off, true/false, 1/0)
- 🧹 **Código Otimizado** - Removidas duplicações, +eficiência

## 📋 Pré-requisitos

### Software:
- **Python 3.8+** (testado com Python 3.13)
- **Node.js 14+** e npm
- **Node-RED** rodando em `http://localhost:1880`

### Hardware (para controle GPIO):
- **Raspberry Pi** com GPIO (qualquer modelo)
- **LEDs, relés, sensores** conectados aos pinos GPIO 2-27
- **Componentes eletrônicos** (resistores, jumpers, protoboard)

### Bibliotecas Python:
```
mcp>=1.19.0
httpx>=0.27.0
```

## 🚀 Instalação Rápida (5 minutos)

### 1️⃣ **Instalar Node-RED**

```bash
# Windows/Mac/Linux
npm install -g node-red

# Iniciar Node-RED
node-red
```

Acesse: `http://localhost:1880`

### 2️⃣ **Configurar Ambiente Python**

```bash
# Navegar para o diretório do projeto
cd mcp-node-red

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Verificar dependências
pip list | findstr mcp
```

### 3️⃣ **Executar Demo**

```bash
# Testar todas as funcionalidades
python demo_completa.py
```

## 🎯 Exemplos de Uso

### 💡 **Exemplo 1: Controle GPIO Individual**

```python
# Ligar LED no pino GPIO 20
control_gpio_mcp({
    "pin": 20,
    "state": "on"
})

# Desligar LED no pino GPIO 21
control_gpio_mcp({
    "pin": 21, 
    "state": "off"
})
```

### 🔥 **Exemplo 2: Controle Múltiplas GPIOs**

```python
# Controlar várias GPIOs simultaneamente
control_multiple_gpio_mcp({
    "gpios": [
        {"pin": 20, "state": "on"},   # LED 1 ligado
        {"pin": 21, "state": "off"},  # LED 2 desligado
        {"pin": 22, "state": "on"},   # Relé ligado
        {"pin": 23, "state": "off"}   # Ventilador desligado
    ]
})
```

### 📊 **Exemplo 3: Verificar Status**

```python
# Ver status de todas as GPIOs
get_gpio_status_mcp({})

# Resposta:
{
    "tool": "gpio_status",
    "result": {
        "pin_mode": "BCM",
        "available_pins": [2,3,4,5,...,27],
        "active_pins": [20, 21, 22],
        "states": {
            "20": {"state": "on", "value": 1, "timestamp": "2025-10-28T..."},
            "21": {"state": "off", "value": 0, "timestamp": "2025-10-28T..."}
        }
    }
}
```

### 🚀 **Exemplo 4: Deploy Flow Completo**

```python
# Implantar flow MCP GPIO completo automaticamente
deploy_mcp_gpio_flow({
    "node_red_url": "http://192.168.0.36:1880"
})
```

### 🎛️ **Exemplo 5: Criar Flow Personalizado**

```python
# Criar flow customizado
create_node_red_flow({
    "flow_name": "Sistema de Automação",
    "nodes": [
        {
            "type": "inject",
            "name": "Timer Automático",
            "config": {
                "payload": "true",
                "repeat": "10"  # A cada 10 segundos
            }
        },
        {
            "type": "rpi-gpio out",
            "name": "LED Status",  
            "config": {
                "pin": "20",
                "bcm": true
            }
        }
    ]
})
```

## 🌐 API MCP Endpoints

Após o deploy do flow MCP GPIO, os seguintes endpoints ficam disponíveis:

### � **POST `/mcp/gpio/control`** - Controle GPIO

```bash
# Ligar GPIO 20
curl -X POST http://localhost:1880/mcp/gpio/control \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "control_gpio",
    "params": {
      "pin": 20,
      "state": "on"
    }
  }'

# Controlar múltiplas GPIOs
curl -X POST http://localhost:1880/mcp/gpio/control \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "control_multiple_gpio", 
    "params": {
      "gpios": [
        {"pin": 20, "state": "on"},
        {"pin": 21, "state": "off"}
      ]
    }
  }'
```

### 📊 **GET `/mcp/gpio/status`** - Status das GPIOs

```bash
curl http://localhost:1880/mcp/gpio/status
```

**Resposta:**
```json
{
  "tool": "gpio_status",
  "result": {
    "pin_mode": "BCM",
    "available_pins": [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
    "active_pins": [20, 21],
    "states": {
      "20": {"state": "on", "value": 1, "timestamp": "2025-10-28T12:34:56.789Z"},
      "21": {"state": "off", "value": 0, "timestamp": "2025-10-28T12:34:56.789Z"}
    }
  }
}
```

### 🛠️ **GET `/mcp/tools`** - Listar Ferramentas

```bash
curl http://localhost:1880/mcp/tools
```

## 💬 Uso com Gemini/Claude CLI

### Configuração Gemini:

```bash
# Instalar e configurar
npm install -g @google/generative-ai-cli
gemini auth
```

### Configuração Claude Desktop:

Adicione ao `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "node-red": {
      "command": "C:/caminho/para/venv/Scripts/python.exe",
      "args": ["C:/caminho/para/main.py"],
      "cwd": "C:/caminho/para/projeto"
    }
  }
}
```

### 🗣️ Exemplos de Comandos por Voz/Texto:

```bash
# Controle básico de GPIO
"Ligue o LED no pino 20"                    → control_gpio_mcp(pin=20, state="on")
"Desligue o relé do pino 21"               → control_gpio_mcp(pin=21, state="off")

# Controle múltiplo
"Ligue os LEDs dos pinos 20, 21 e 22"      → control_multiple_gpio_mcp()
"Desligue todos os dispositivos"            → control_multiple_gpio_mcp()

# Status e monitoramento
"Qual o status das GPIOs?"                  → get_gpio_status_mcp()
"Me mostre o estado do pino 20"            → get_gpio_status_mcp()

# Deploy e configuração
"Instale o flow MCP GPIO completo"         → deploy_mcp_gpio_flow()
"Configure o sistema de automação"          → create_node_red_flow()

# Comandos avançados com contexto
"Crie um flow que pisca o LED do pino 20 a cada 5 segundos"
"Configure um sistema de alarme com os pinos 20, 21 e 22"
"Faça backup do flow atual e crie um novo para controle de temperatura"
```

## 📁 Estrutura do Projeto

```
node-red-gemini/
├── main.py                          # 🚀 Servidor MCP principal (13 ferramentas)
├── demo_completa.py                 # 🧪 Demonstração completa 
├── deploy_mcp_gpio_flow.py          # 🔧 Deploy automático flow MCP GPIO
├── validar_main.py                  # ✅ Script de validação
│
├── flows_mcp_gpio_completo.json     # 🎯 Flow MCP GPIO completo
├── requirements.txt                 # 📦 Dependências Python
├── mcp-config.json                  # ⚙️  Configuração MCP
│
├── README.md                        # 📖 Esta documentação
├── QUICKSTART.md                    # ⚡ Guia rápido (5 min)
├── RASPBERRY_PI_LED_GUIDE.md        # 🔌 Guia GPIO Raspberry Pi
├── LIMPEZA_FERRAMENTAS.md           # 🧹 Log de otimizações v2.0
│
└── .venv/                      # Ambiente virtual Python
```

## 🔧 Scripts Disponíveis

### 1. **Servidor MCP** (main.py)
```bash
python main.py
```
Inicia o servidor MCP via stdio. Usado por clientes MCP (Gemini CLI, VS Code, etc.)

### 2. **Demo Completa** (demo_completa.py)
```bash
python demo_completa.py
```
Demonstra todas as 10 funcionalidades do servidor:
- ✅ Criar flows
- ✅ Listar flows
- ✅ Obter detalhes
- ✅ Export/Import
- ✅ Deploy automático

### 3. **Criar Flow LED** (criar_flow_led.py)
```bash
python criar_flow_led.py
```
Cria automaticamente um flow completo para controle de LED via GPIO no Raspberry Pi.

### 4. **Validar** (validar_main.py)
```bash
python validar_main.py
```
Valida que o servidor MCP está configurado corretamente.

## 🍓 Raspberry Pi - Controle de LED

### Conexão Hardware:

```
Raspberry Pi GPIO
┌──────────────────┐
│  GPIO 17  ●──────┼──── Resistor 220Ω ──── LED (+)
│  GND      ●──────┼──────────────────────── LED (-)
└──────────────────┘
```

### Criar Flow LED:

```bash
python criar_flow_led.py
```

### Usar com Gemini:

```bash
# Ligar LED
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "acenda o led"

# Desligar LED
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "apague o led"
```

Para guia completo, veja: **[RASPBERRY_PI_LED_GUIDE.md](RASPBERRY_PI_LED_GUIDE.md)**

## 🔌 Integração VS Code

Adicione em `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "node-red": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/caminho/para/mcp-node-red"
    }
  }
}
```

## 🐛 Troubleshooting

### ❌ Node-RED não conecta

```bash
# Verificar se está rodando
curl http://localhost:1880/flows

# Iniciar Node-RED
node-red
```

### ❌ Erro de importação

```bash
# Ativar ambiente
.venv\Scripts\activate

# Reinstalar dependências
pip install -r requirements.txt
```

### ❌ LED não responde (Raspberry Pi)

```bash
# Verificar permissões GPIO
sudo usermod -a -G gpio $USER
sudo reboot

# Testar GPIO manualmente
gpio -g mode 17 out
gpio -g write 17 1  # Ligar
gpio -g write 17 0  # Desligar
```

## 📊 Arquitetura do Sistema

```
┌─────────────────────────────────┐
│   USUÁRIO / CLIENTE              │
│   (Gemini CLI, VS Code)          │
└──────────────┬──────────────────┘
               │ MCP Protocol
               ↓
┌─────────────────────────────────┐
│   SERVIDOR MCP (main.py)         │
│   • Gerencia ferramentas         │
│   • Processa comandos            │
└──────────────┬──────────────────┘
               │ HTTP REST API
               ↓
┌─────────────────────────────────┐
│   NODE-RED                       │
│   • Flows de automação           │
│   • Lógica de negócio            │
└──────────────┬──────────────────┘
               │ GPIO Control
               ↓
┌─────────────────────────────────┐
│   RASPBERRY PI / HARDWARE        │
│   • LED, sensores, atuadores     │
└─────────────────────────────────┘
```

## 🎯 Exemplos Práticos

### Exemplo 1: Criar Flow de Monitoramento

```python
# Via Python (usando nossa API)
import asyncio
import httpx

async def criar_flow():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:1880/flows",
            json={
                "flow_name": "Monitoramento",
                "nodes": [
                    {"type": "inject", "name": "Timer"},
                    {"type": "http request", "name": "API Check"},
                    {"type": "debug", "name": "Log"}
                ]
            }
        )
        print(response.json())

asyncio.run(criar_flow())
```

### Exemplo 2: Controle via Gemini CLI

```bash
# Linguagem natural para controle
gemini --mcp mcp://localhost:1880/mcp-led \
  "acenda o led quando a temperatura passar de 25 graus"
```

## � Início Rápido

### 1️⃣ **Clone e Configure**

```bash
git clone https://github.com/Luiznunes13/node-red-gemini.git
cd node-red-gemini

# Ativar ambiente virtual
.venv/Scripts/activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# Verificar dependências
pip list | grep mcp
```

### 2️⃣ **Iniciar Node-RED**

```bash
node-red
# Aguarde: "Server now running at http://127.0.0.1:1880/"
```

### 3️⃣ **Executar Servidor MCP**

```bash
python main.py
```

### 4️⃣ **Deploy Flow MCP GPIO (opcional)**

```bash
python deploy_mcp_gpio_flow.py
```

### 5️⃣ **Testar**

```bash
# Via curl
curl -X POST http://localhost:1880/mcp/gpio/control \
  -H "Content-Type: application/json" \
  -d '{"tool": "control_gpio", "params": {"pin": 20, "state": "on"}}'

# Via Python
python demo_completa.py
```

## 📚 Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| 📖 **[QUICKSTART.md](QUICKSTART.md)** | ⚡ Início ultra-rápido (5 min) |
| 📖 **[RASPBERRY_PI_LED_GUIDE.md](RASPBERRY_PI_LED_GUIDE.md)** | 🔌 Guia GPIO completo |
| 📖 **[LIMPEZA_FERRAMENTAS.md](LIMPEZA_FERRAMENTAS.md)** | 🧹 Otimizações v2.0 |
| 📖 **[Model Context Protocol](https://modelcontextprotocol.io/)** | 🌐 Especificação MCP oficial |
| 📖 **[Node-RED Docs](https://nodered.org/docs/)** | 🎛️ Documentação Node-RED |

## 🆕 Changelog v2.0

### ✨ **Novidades**
- 🔥 **API MCP GPIO Completa** - Controle de todos os pinos GPIO (2-27)
- ⚡ **Controle Múltiplo** - Múltiplas GPIOs simultaneamente  
- 📊 **Status Global** - Monitoramento centralizado
- 🌐 **Endpoints RESTful** - `/mcp/gpio/control`, `/mcp/gpio/status`, `/mcp/tools`
- 🚀 **Deploy Automático** - `deploy_mcp_gpio_flow.py`

### � **Otimizações**
- ❌ Removidas 2 ferramentas duplicadas/obsoletas
- ✅ Mantidas 13 ferramentas otimizadas
- 🛡️ Validação robusta de parâmetros
- 📈 Performance melhorada

## �🤝 Contribuindo

Contribuições são muito bem-vindas! 

### Como contribuir:
1. **Fork** o projeto ⭐
2. **Clone** seu fork 📥
3. **Crie** uma branch (`git checkout -b feature/amazing-feature`) 🌿
4. **Commit** suas mudanças (`git commit -m 'Add amazing feature'`) 💾
5. **Push** para a branch (`git push origin feature/amazing-feature`) 🚀
6. **Abra** um Pull Request 🔄

### Áreas que precisam de ajuda:
- 🔌 Novos tipos de sensores/atuadores
- 🌐 Integração com mais plataformas IoT  
- 📱 Interface mobile para controle
- 🧪 Testes automatizados
- 📖 Tradução da documentação

## ⭐ Reconhecimentos

- **MCP Team** - Protocol specification
- **Node-RED Community** - Amazing visual programming
- **Raspberry Pi Foundation** - GPIO hardware
- **Google Gemini** - AI integration
- **Anthropic Claude** - MCP development support

## 📄 Licença

Este projeto está sob a **licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

**🎉 Feito com ❤️ para a comunidade IoT e automação residencial!**

*Se este projeto te ajudou, considere dar uma ⭐ no GitHub!*

## ✨ Status do Projeto

- **Status:** ✅ Funcional e Testado
- **Versão:** 1.0.0
- **Python:** 3.8+
- **Node-RED:** 4.0+
- **MCP:** 1.19.0

---

**Desenvolvido com ❤️ usando Python, Node-RED e MCP**

**Data:** Outubro 2025
