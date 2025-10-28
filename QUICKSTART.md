# ⚡ QUICK START - MCP Node-RED

## 🚀 Início Rápido (5 minutos)

### 1️⃣ **Pré-requisitos**
```bash
# Verificar se tem Python 3.8+
python --version

# Verificar se tem Node.js
node --version
```

### 2️⃣ **Instalar Node-RED**
```bash
npm install -g node-red
```

### 3️⃣ **Configurar Projeto**
```bash
# Clonar/baixar projeto
cd mcp-node-red

# Ativar ambiente virtual
.venv\Scripts\activate

# Verificar dependências
pip list
```

### 4️⃣ **Iniciar Node-RED**
```bash
# Terminal 1
node-red

# Aguarde até ver: "Server now running at http://127.0.0.1:1880/"
```

### 5️⃣ **Executar Demo**
```bash
# Terminal 2
python demo_completa.py
```

## 🎯 **Comandos Úteis**

### **Testar Tudo:**
```bash
python demo_completa.py
```

### **Criar Flow LED:**
```bash
python criar_flow_led.py
```

### **Testar HTTP:**
```bash
python teste_http_simples.py
```

### **Verificar Node-RED:**
```bash
# No navegador:
http://localhost:1880
```

## 🔧 **Solução Rápida de Problemas**

### ❌ **"Node-RED não está rodando"**
```bash
# Iniciar Node-RED
node-red

# Ou verificar porta
netstat -an | findstr "1880"
```

### ❌ **"Módulo não encontrado"**
```bash
# Ativar ambiente
.venv\Scripts\activate

# Reinstalar dependências
pip install -r requirements.txt
```

### ❌ **"Endpoint 404"**
```bash
# Fazer deploy manual
python deploy_e_testar.py
```

## 📚 **Documentação Completa**

- 📖 **README.md** - Guia principal
- 📖 **RASPBERRY_PI_LED_GUIDE.md** - Para Raspberry Pi
- 📖 **PROJETO_FINAL.md** - Visão completa

## ✅ **Checklist de Validação**

- [ ] Python instalado
- [ ] Node.js instalado
- [ ] Node-RED rodando
- [ ] Ambiente virtual ativado
- [ ] Demo executado com sucesso
- [ ] Flows criados no Node-RED

## 🎉 **Tudo Funcionando?**

Se todos os ✅ acima estiverem OK, você está pronto!

**Próximo passo:** Explore os scripts e crie seus próprios flows!

---

**Tempo estimado:** 5-10 minutos
**Dificuldade:** 🟢 Fácil
**Suporte:** Veja PROJETO_FINAL.md para detalhes
