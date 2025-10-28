# 🚀 Servidor MCP para Node-RED

Servidor Model Context Protocol (MCP) para automação e controle do Node-RED via linguagem natural, incluindo controle de dispositivos IoT como LED no Raspberry Pi.

## ⭐ Funcionalidades Principais

### 🔧 **10 Ferramentas MCP Disponíveis:**

| # | Ferramenta | Descrição |
|---|------------|-----------|
| 1 | `create_node_red_flow` | Cria novos flows no Node-RED |
| 2 | `get_node_red_flow` | Obtém informações de flow específico |
| 3 | `update_node_red_flow` | Atualiza flows existentes |
| 4 | `delete_node_red_flow` | Remove flows do Node-RED |
| 5 | `deploy_node_red_flows` | Faz deploy automático de flows |
| 6 | `get_node_red_nodes` | Lista tipos de nós disponíveis |
| 7 | `export_node_red_flow` | Exporta flow para arquivo JSON |
| 8 | `import_node_red_flow` | Importa flow de arquivo JSON |
| 9 | `control_raspberry_pi_led` | Controla LED via GPIO |
| 10 | `create_raspberry_pi_led_flow` | Cria flow LED completo |

### 🎯 **Casos de Uso:**

- ✅ **Automação Residencial** - Controle por voz/texto
- ✅ **IoT e Raspberry Pi** - Controle de hardware GPIO
- ✅ **Gerenciamento Visual** - Node-RED interface
- ✅ **Integração IA** - Gemini CLI com linguagem natural
- ✅ **Prototipagem Rápida** - Deploy automático

## 📋 Pré-requisitos

### Software:
- **Python 3.8+** (testado com Python 3.13)
- **Node.js 14+** e npm
- **Node-RED** rodando em `http://localhost:1880`

### Hardware (opcional para controle LED):
- Raspberry Pi com GPIO
- LED e resistor 220Ω

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

## 📝 Exemplos de Uso

### Exemplo 1: Criar um Flow Simples

```python
# Usar a ferramenta create_node_red_flow
{
    "flow_name": "Meu Primeiro Flow",
    "nodes": [
        {
            "type": "inject",
            "name": "Timer",
            "config": {
                "payload": "Hello World",
                "repeat": "5"
            }
        },
        {
            "type": "debug",
            "name": "Console"
        }
    ]
}
```

### Exemplo 2: Exportar um Flow

```python
# Usar a ferramenta export_node_red_flow
{
    "flow_id": "abc123",
    "file_path": "./exported_flow.json"
}
```

### Exemplo 3: Importar um Flow

```python
# Usar a ferramenta import_node_red_flow
{
    "file_path": "./my_flow.json",
    "flow_name": "Flow Importado"
}
```

## 💬 Uso com Gemini CLI

### Instalação Gemini CLI:

```bash
npm install -g @google/generative-ai-cli

# Autenticar
gemini auth
```

### Exemplos de Comandos:

```bash
# Controlar LED no Raspberry Pi
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "acenda o led"
gemini --mcp mcp://<ip-do-pi>:1880/mcp-led "apague a luz"

# Variações em linguagem natural
gemini --mcp mcp://localhost:1880/mcp-led "por favor, ligue o led vermelho"
gemini --mcp mcp://localhost:1880/mcp-led "desligue tudo"
```

## 📁 Estrutura do Projeto

```
mcp-node-red/
├── main.py                      # Servidor MCP principal
├── demo_completa.py             # Demonstração de funcionalidades
├── criar_flow_led.py            # Gerador de flow LED para Raspberry Pi
├── validar_main.py              # Script de validação
│
├── requirements.txt             # Dependências Python
├── mcp-config.json             # Configuração MCP
│
├── README.md                    # Esta documentação
├── QUICKSTART.md               # Guia rápido
├── RASPBERRY_PI_LED_GUIDE.md   # Guia completo Raspberry Pi
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

## 📚 Documentação Adicional

- 📖 **[QUICKSTART.md](QUICKSTART.md)** - Início rápido (5 min)
- 📖 **[RASPBERRY_PI_LED_GUIDE.md](RASPBERRY_PI_LED_GUIDE.md)** - Guia completo Raspberry Pi
- 📖 **[Model Context Protocol](https://modelcontextprotocol.io/)** - Especificação MCP
- 📖 **[Node-RED Docs](https://nodered.org/docs/)** - Documentação Node-RED

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## ✨ Status do Projeto

- **Status:** ✅ Funcional e Testado
- **Versão:** 1.0.0
- **Python:** 3.8+
- **Node-RED:** 4.0+
- **MCP:** 1.19.0

---

**Desenvolvido com ❤️ usando Python, Node-RED e MCP**

**Data:** Outubro 2025
