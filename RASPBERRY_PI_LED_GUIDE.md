# 🔴 Controlando um LED no Raspberry Pi com Gemini CLI, MCP e Node-RED

## 📋 Visão Geral da Arquitetura

Este guia descreve como usar **linguagem natural** (via Gemini CLI) para controlar um dispositivo físico (um LED) conectado a um Raspberry Pi, usando o Node-RED como servidor e o Model Context Protocol (MCP) como ponte de comunicação.

### 🔄 Fluxo de Comando

```
Usuário (Gemini CLI)
        ↓ "acenda o led"
Gemini CLI (com MCP)
        ↓ conecta via MCP
Node-RED (Servidor MCP)
        ↓ processa comando
Raspberry Pi (GPIO)
        ↓ controla hardware
LED 💡 (Liga/Desliga)
```

## 🛠️ Pré-requisitos

### Hardware Necessário:
- ✅ **Raspberry Pi** (qualquer modelo com GPIO)
- ✅ **LED** (qualquer cor)
- ✅ **Resistor** 220Ω ou 330Ω
- ✅ **Jumpers** para conexão

### Software Necessário:
- ✅ **Node-RED** instalado no Raspberry Pi
- ✅ **node-red-node-pi-gpio** (nó GPIO para Node-RED)
- ✅ **Gemini CLI** (em qualquer máquina na mesma rede)
- ✅ **Nosso Servidor MCP** (este projeto)

## 🔌 Passo 1: Configurar o Hardware

### Diagrama de Conexão:

```
Raspberry Pi GPIO
┌──────────────────┐
│                  │
│  GPIO 17  ●──────┼──── Resistor 220Ω ──── LED (anodo +)
│                  │
│  GND      ●──────┼──────────────────────── LED (catodo -)
│                  │
└──────────────────┘
```

### Conexões Físicas:
1. **Pino GPIO 17** → Resistor 220Ω → **Perna longa do LED** (anodo +)
2. **Pino GND** → **Perna curta do LED** (catodo -)

### ⚠️ Importante:
- O resistor é **obrigatório** para limitar a corrente e proteger o LED
- GPIO 17 é o pino físico 11 no Raspberry Pi
- Você pode usar outro pino GPIO, basta ajustar a configuração

## 🚀 Passo 2: Instalar Dependências no Raspberry Pi

### 2.1. Instalar Node-RED (se ainda não tiver):

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```

### 2.2. Instalar o nó GPIO:

```bash
cd ~/.node-red
npm install node-red-node-pi-gpio
```

### 2.3. Iniciar Node-RED:

```bash
node-red-start
```

Acesse: `http://<ip-do-pi>:1880`

## 📝 Passo 3: Criar o Flow no Node-RED

### 3.1. Flow Básico de Teste

Cole este JSON no Node-RED (Menu → Import):

```json
[
    {
        "id": "led-flow-tab",
        "type": "tab",
        "label": "Controle LED MCP",
        "disabled": false
    },
    {
        "id": "inject-on",
        "type": "inject",
        "z": "led-flow-tab",
        "name": "Ligar LED",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "1",
        "payloadType": "num",
        "x": 140,
        "y": 100,
        "wires": [["gpio-led"]]
    },
    {
        "id": "inject-off",
        "type": "inject",
        "z": "led-flow-tab",
        "name": "Desligar LED",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "0",
        "payloadType": "num",
        "x": 140,
        "y": 160,
        "wires": [["gpio-led"]]
    },
    {
        "id": "gpio-led",
        "type": "rpi-gpio out",
        "z": "led-flow-tab",
        "name": "GPIO 17 - LED",
        "pin": "11",
        "set": true,
        "level": "0",
        "freq": "",
        "out": "out",
        "bcm": false,
        "x": 380,
        "y": 130,
        "wires": []
    }
]
```

### 3.2. Testar o Flow

1. Clique no botão **"Ligar LED"** - O LED deve acender 💡
2. Clique no botão **"Desligar LED"** - O LED deve apagar

Se funcionar, ótimo! Seu hardware está OK. ✅

## 🤖 Passo 4: Integrar com MCP

### 4.1. Criar Flow MCP Completo

Use nosso servidor MCP para criar o flow automaticamente:

```python
# Exemplo de código Python usando nosso MCP
import asyncio
import httpx

async def criar_flow_led():
    async with httpx.AsyncClient() as client:
        # Criar flow completo com MCP
        response = await client.post(
            "http://localhost:1880/mcp/create_flow",
            json={
                "flow_name": "LED MCP Control",
                "gpio_pin": 17,
                "enable_mcp": True
            }
        )
        print(response.json())

asyncio.run(criar_flow_led())
```

### 4.2. Flow com Endpoint MCP

O flow MCP deve ter:

1. **HTTP IN** - Recebe comandos via HTTP
2. **Function Node** - Processa comando de linguagem natural
3. **GPIO OUT** - Controla o LED

```json
{
  "functions": [
    {
      "name": "setLedState",
      "description": "Define o estado do LED (ligado ou desligado)",
      "parameters": {
        "type": "OBJECT",
        "properties": {
          "state": {
            "type": "STRING",
            "description": "O estado desejado para o LED",
            "enum": ["on", "off"]
          }
        },
        "required": ["state"]
      }
    }
  ]
}
```

## 💬 Passo 5: Usar com Gemini CLI

### 5.1. Instalar Gemini CLI (se ainda não tiver):

```bash
npm install -g @google/generative-ai-cli
```

### 5.2. Configurar autenticação:

```bash
gemini auth
```

### 5.3. Comandos de Exemplo:

```bash
# Ligar o LED
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "acenda o led"

# Desligar o LED
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "apague a luz"

# Variações em linguagem natural
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "por favor, ligue o led vermelho"
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "desligue tudo"
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "quero que a luz fique acesa"
```

## 🎯 Como Funciona Internamente

### Sequência de Eventos:

1. **Usuário fala**: "acenda o led"
   
2. **Gemini CLI**:
   - Conecta em `mcp://<ip-do-pi>:1880/mcp-led`
   - Obtém o modelo de contexto (schema da função)
   
3. **API Gemini**:
   - Analisa o prompt + contexto
   - Identifica: "usuário quer ligar → chamar setLedState(state='on')"
   
4. **Node-RED**:
   - Recebe: `{"function": "setLedState", "arguments": {"state": "on"}}`
   - Function node converte: `"on"` → `1`
   - Envia para GPIO
   
5. **Raspberry Pi**:
   - GPIO 17 recebe `HIGH` (3.3V)
   - LED acende 💡

### Function Node (Lógica):

```javascript
// Recebe do MCP
let args = msg.payload.arguments;

// Converte para GPIO
if (args && args.state) {
  if (args.state === "on") {
    msg.payload = 1; // HIGH
  } else if (args.state === "off") {
    msg.payload = 0; // LOW
  }
  return msg;
}

return null;
```

## 🔧 Troubleshooting

### LED não acende:

1. ✅ Verifique as conexões físicas
2. ✅ Teste com os botões inject no Node-RED
3. ✅ Verifique se o pino GPIO está correto (físico 11 = GPIO 17)
4. ✅ Verifique polaridade do LED (perna longa = +)

### Node-RED não responde:

1. ✅ Verifique se está rodando: `node-red-log`
2. ✅ Teste acesso: `http://<ip-do-pi>:1880`
3. ✅ Verifique firewall

### Gemini CLI não conecta:

1. ✅ Verifique URL do MCP endpoint
2. ✅ Teste manualmente: `curl http://<ip-do-pi>:1880/mcp-led`
3. ✅ Verifique autenticação do Gemini

### Permissões GPIO:

```bash
# Adicionar usuário ao grupo gpio
sudo usermod -a -G gpio $USER

# Reiniciar para aplicar
sudo reboot
```

## 🎨 Expansões Possíveis

### 1. Múltiplos LEDs:

```python
# Controlar LED RGB
gemini --mcp ... "acenda o led vermelho"
gemini --mcp ... "acenda o led verde"
gemini --mcp ... "faça o led piscar azul"
```

### 2. Sensores:

```python
# Ler temperatura
gemini --mcp ... "qual a temperatura atual?"

# Ler umidade
gemini --mcp ... "está muito úmido?"
```

### 3. Automação:

```python
# Criar regras
gemini --mcp ... "acenda o led quando escurecer"
gemini --mcp ... "desligue tudo às 22h"
```

### 4. Dashboard:

```bash
# Instalar dashboard
cd ~/.node-red
npm install node-red-dashboard

# Criar interface visual
```

## 📚 Recursos Adicionais

- 📖 [Documentação Node-RED GPIO](https://flows.nodered.org/node/node-red-node-pi-gpio)
- 📖 [Pinout Raspberry Pi](https://pinout.xyz/)
- 📖 [MCP Protocol Spec](https://modelcontextprotocol.io/)
- 📖 [Gemini CLI Docs](https://ai.google.dev/gemini-api/docs/cli)

## ✅ Checklist Final

- [ ] Hardware conectado corretamente
- [ ] Node-RED instalado e rodando
- [ ] Nó GPIO instalado
- [ ] Flow de teste funcionando (botões inject)
- [ ] Flow MCP criado e deployado
- [ ] Gemini CLI instalado e autenticado
- [ ] Comando via Gemini funciona
- [ ] LED responde a comandos de linguagem natural

## 🎉 Conclusão

Parabéns! Você agora tem um sistema completo de controle por voz/texto usando:
- 🤖 IA (Gemini)
- 🔧 MCP (Protocolo de Contexto)
- 🔴 Node-RED (Automação)
- 🍓 Raspberry Pi (Hardware)
- 💡 LED (Dispositivo Físico)

**Status:** 🚀 PRONTO PARA USO!
