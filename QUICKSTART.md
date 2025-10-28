# ⚡ QUICK START - MCP Node-RED GPIO

**🎯 Objetivo:** Configurar o servidor MCP, integrar com Gemini CLI e controlar GPIO em **3 minutos**!

## 📋 Pré-requisitos

✅ Python 3.8+ instalado  
✅ Node.js 14+ e npm instalados  
✅ Node-RED rodando (`npm install -g node-red`)

## 📦 Arquivos Incluídos

O projeto já vem com tudo pronto:

```
node-red-gemini/
├── main.py                    # 🚀 Servidor MCP (já configurado)
├── mcp_all_gpios.json         # 🎯 Flow Node-RED pronto (importar)
├── deploy_mcp_gpio_flow.py    # 🔧 Deploy automático (opcional)
├── .venv/                     # 🐍 Ambiente Python (já instalado)
└── requirements.txt           # 📦 Dependências (já instaladas)
```

💡 **Você só precisa:**
1. Ativar o ambiente Python
2. Importar o flow no Node-RED
3. Instalar a paleta GPIO
4. Testar!

## 🚀 Setup Rápido (3 passos)

### 1️⃣ **Configurar Servidor MCP**

```bash
# Navegar para o projeto
cd node-red-gemini

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Verificar que as dependências estão instaladas
pip list | grep mcp
# Deve mostrar: mcp 1.8.1 ou superior
```

### 2️⃣ **Configurar Node-RED**

```bash
# Iniciar Node-RED em um terminal separado
node-red

# ✅ Aguarde: "Server now running at http://127.0.0.1:1880/"
```

**Instalar paleta GPIO (necessário para Raspberry Pi):**

1. Abra o navegador em `http://localhost:1880`
2. Clique no menu **☰** (canto superior direito)
3. Selecione **"Manage palette"**
4. Vá para a aba **"Install"**
5. Busque por: `node-red-node-pi-gpio`
6. Clique em **"Install"** ([ver no flows.nodered.org](https://flows.nodered.org/node/node-red-node-pi-gpio))

**Importar Flow MCP GPIO:**

1. No Node-RED, clique no menu **☰** → **"Import"**
2. Selecione a aba **"select a file to import"**
3. Escolha o arquivo: `mcp_all_gpios.json` (na raiz do projeto)
4. Clique em **"Import"**
5. Clique em **"Deploy"** (botão vermelho no topo)

### 3️⃣ **Configurar Gemini CLI**

```bash
# Instalar Gemini CLI
npx https://github.com/google-gemini/gemini-cli

# Configurar servidor MCP no Gemini
# Editar: C:\Seu\<USER>\.gemini\settings.json
```

**Adicione ao `settings.json`:**
```json
{
  "mcpServers": {
    "node-red": {
      "command": "C:/Seu/caminho/Documentos/Projetos/node-red-gemini/.venv/Scripts/python.exe",
      "args": ["C:/Seu/caminho/Documentos/Projetos/node-red-gemini/main.py"],
      "cwd": "C:/Seu/caminho/Documentos/Projetos/node-red-gemini"
    }
  }
}
```

💡 **Dica:** Ajuste os caminhos para seu sistema!

## ✨ Testar Agora

### 🧪 **Teste 1: Servidor MCP funcionando**

```bash
# No Gemini CLI
gemini chat

# Digite no chat:
"ligue o led no gpio 28 do nodered 192.168.0.36:1880"
```

**✅ Resultado esperado:** GPIO 20 controlada com sucesso!

### 🔥 **Teste 2: Controle múltiplo**

```bash
# No Gemini CLI chat:
"ligue os leds dos pinos 20, 21 e 22"
```

**✅ Resultado:** Múltiplas GPIOs controladas!

### 📊 **Teste 3: Status**

```bash
# No Gemini CLI chat:
"qual o status das gpios?"
```

**✅ Resultado:** Status completo de todas as GPIOs!


## 🎯 Comandos Úteis Gemini CLI

### 💬 **Controle por Linguagem Natural:**

```bash
# Ligar dispositivos
"ligue o led do pino 20"
"acenda a luz do gpio 21"
"ative o relé no pino 22"

# Desligar dispositivos
"desligue o led do pino 20"
"apague tudo"
"desative os pinos 20, 21 e 22"

# Status e monitoramento
"qual o status do gpio 20?"
"me mostre o estado de todas as gpios"
"quantos pinos estão ativos?"

# Automação
"crie um flow que pisca o led do pino 20 a cada 5 segundos"
"configure um sistema de alarme com os pinos 20 e 21"
```

## 🔧 Comandos Avançados (Opcional)

### 📜 **Deploy via Script Python:**

Se preferir deploy automático via código:

```bash
python deploy_mcp_gpio_flow.py
```

Isso fará o deploy programático do flow (alternativa ao import manual).

### 🌐 **Endpoints REST Disponíveis:**

Após importar o flow `mcp_all_gpios.json`:

- `POST http://localhost:1880/mcp/gpio/control` - Controlar GPIOs
- `GET http://localhost:1880/mcp/gpio/status` - Ver status
- `GET http://localhost:1880/mcp/tools` - Listar ferramentas

## 🧪 Teste via curl (Alternativa)

```bash
# Ligar GPIO 20
curl -X POST http://localhost:1880/mcp/gpio/control \
  -H "Content-Type: application/json" \
  -d '{"tool": "control_gpio", "params": {"pin": 20, "state": "on"}}'

# Ver status
curl http://localhost:1880/mcp/gpio/status
```

## 🔧 Solução Rápida de Problemas

### ❌ **"Node-RED não conecta"**
```bash
# Verificar se está rodando
node-red

# Testar navegador
http://localhost:1880
```

### ❌ **"Servidor MCP não responde"**
```bash
# Verificar caminho no settings.json
# Testar servidor manualmente
python main.py
```

### ❌ **"Gemini não encontra ferramentas"**
```bash
# Reiniciar Gemini CLI após editar settings.json
# Verificar logs: C:\Seu\<USER>\.gemini\logs\
```

### ❌ **"Erro de GPIO no Raspberry Pi"**
```bash
# Via Node-RED UI (Recomendado):
# Menu ☰ → Manage palette → Install → node-red-node-pi-gpio

# Ou via linha de comando:
cd ~/.node-red
npm install node-red-node-pi-gpio

# Reiniciar Node-RED
node-red-stop
node-red-start
```

### ❌ **"Flow não importado"**
```bash
# Verificar se o arquivo mcp_all_gpios.json existe
ls mcp_all_gpios.json

# Importar manualmente:
# 1. Copie o conteúdo do arquivo
# 2. Node-RED → Menu ☰ → Import → Clipboard
# 3. Cole o JSON → Import → Deploy
```

## 📊 Verificar se está tudo OK

### ✅ **Checklist Rápido:**

```bash
# 1. Python ambiente ativo
.venv\Scripts\activate
python --version  # Deve mostrar 3.8+

# 2. Node-RED rodando
curl http://localhost:1880  # Deve retornar HTML

# 3. Flow MCP importado
# Abra http://localhost:1880 e veja a aba "MCP GPIO - Todas as GPIOs"

# 4. Paleta GPIO instalada
# Node-RED → Menu ☰ → Manage palette → "node-red-node-pi-gpio" deve estar na lista

# 5. Dependências MCP instaladas
pip list | grep mcp  # Deve mostrar mcp>=1.19.0

# 6. Gemini configurado
cat ~/.gemini/settings.json  # Deve ter mcpServers.node-red

# 7. Testar ferramenta
gemini chat
> "teste o servidor mcp node-red"
```

### 🎯 **Teste Completo:**

```bash
# Teste end-to-end completo
curl -X POST http://localhost:1880/mcp/gpio/control \
  -H "Content-Type: application/json" \
  -d '{"tool": "control_gpio", "params": {"pin": 20, "state": "on"}}'

# ✅ Deve retornar: {"tool":"control_gpio","result":{"success":true,...}}
```

## 🎓 Próximos Passos

Agora que está funcionando:

1. 📖 **Explore o README.md** - Documentação completa
2. � **Veja RASPBERRY_PI_LED_GUIDE.md** - Hardware GPIO
3. 🧪 **Execute demo_completa.py** - Exemplos práticos
4. 🚀 **Crie seus próprios flows** - Automatize tudo!

## 💡 Dicas Pro

### 🔥 **Atalhos Úteis:**

```bash
# Alias para ativar ambiente (adicione ao .bashrc)
alias mcp-activate='cd ~/node-red-gemini && .venv/Scripts/activate'

# Alias para iniciar tudo
alias mcp-start='node-red & python main.py'

# Alias para testar
alias mcp-test='gemini chat'
```

### ⚡ **Performance:**

- Use `deploy_type: "nodes"` para deploy mais rápido
- Configure `credentialSecret` no Node-RED para segurança
- Monitore logs: `~/.node-red/logs/`

---

**⏱️ Tempo total:** ~3 minutos  
**🎯 Dificuldade:** 🟢 Muito Fácil  
**💬 caminhote:** GitHub Issues ou README.md

🎉 **Pronto! Você está controlando GPIO por voz/texto!**
