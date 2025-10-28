#!/usr/bin/env python3
"""
Gerador Automático de Flow para Controle de LED via MCP
Cria um flow completo no Node-RED para controlar LED no Raspberry Pi
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

NODE_RED_URL = "http://localhost:1880"

async def criar_flow_led_mcp_completo(gpio_pin=17, flow_name="Controle LED via MCP"):
    """
    Cria um flow completo no Node-RED com:
    - HTTP endpoint para MCP
    - Function node para processar comandos
    - GPIO output para controlar LED
    """
    
    print(f"🚀 Criando flow '{flow_name}' para controle de LED...")
    print(f"📍 GPIO Pin: {gpio_pin}")
    print()
    
    # Gerar IDs únicos
    flow_id = str(uuid.uuid4())
    http_in_id = str(uuid.uuid4())
    function_id = str(uuid.uuid4())
    gpio_id = str(uuid.uuid4())
    http_response_id = str(uuid.uuid4())
    
    # 1. Tab do Flow
    flow_tab = {
        "id": flow_id,
        "type": "tab",
        "label": flow_name,
        "disabled": False,
        "info": "Flow para controlar LED via MCP e Gemini CLI"
    }
    
    # 2. HTTP IN - Endpoint MCP
    http_in = {
        "id": http_in_id,
        "type": "http in",
        "z": flow_id,
        "name": "MCP Endpoint",
        "url": "/mcp-led",
        "method": "post",
        "upload": False,
        "swaggerDoc": "",
        "x": 140,
        "y": 140,
        "wires": [[function_id]]
    }
    
    # 3. Function Node - Processa comandos MCP
    function_code = """
// Processa comando MCP do Gemini
// Entrada: { "function": "setLedState", "arguments": { "state": "on" } }

// Se for GET (requisição de modelo)
if (msg.req.method === 'GET') {
    // Retorna o modelo MCP
    msg.payload = {
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
    };
    msg.statusCode = 200;
    return [msg, null]; // Envia para http response
}

// Se for POST (execução de função)
if (msg.req.method === 'POST') {
    let body = msg.payload;
    
    // Verifica se é uma chamada de função
    if (body.function === "setLedState" && body.arguments) {
        let state = body.arguments.state;
        
        // Converte para GPIO (0 ou 1)
        if (state === "on") {
            msg.payload = 1;
            msg.ledState = "ON";
        } else if (state === "off") {
            msg.payload = 0;
            msg.ledState = "OFF";
        } else {
            msg.payload = {
                "error": "Estado inválido. Use 'on' ou 'off'."
            };
            msg.statusCode = 400;
            return [msg, null];
        }
        
        // Prepara resposta de sucesso
        msg.response = {
            "success": true,
            "function": "setLedState",
            "state": state,
            "timestamp": new Date().toISOString()
        };
        
        return [null, msg]; // Envia para GPIO
    }
    
    // Comando não reconhecido
    msg.payload = {
        "error": "Função não reconhecida"
    };
    msg.statusCode = 400;
    return [msg, null];
}

// Método não suportado
msg.payload = {
    "error": "Método não suportado"
};
msg.statusCode = 405;
return [msg, null];
"""
    
    function_node = {
        "id": function_id,
        "type": "function",
        "z": flow_id,
        "name": "Processar MCP",
        "func": function_code,
        "outputs": 2,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 360,
        "y": 140,
        "wires": [[http_response_id], [gpio_id]]
    }
    
    # 4. GPIO OUT - Controla o LED
    gpio_node = {
        "id": gpio_id,
        "type": "rpi-gpio out",
        "z": flow_id,
        "name": f"LED GPIO {gpio_pin}",
        "pin": str(gpio_pin),
        "set": True,
        "level": "0",
        "freq": "",
        "out": "out",
        "bcm": True,
        "x": 590,
        "y": 180,
        "wires": [[http_response_id]]
    }
    
    # 5. HTTP Response
    http_response = {
        "id": http_response_id,
        "type": "http response",
        "z": flow_id,
        "name": "Resposta MCP",
        "statusCode": "",
        "headers": {},
        "x": 780,
        "y": 140,
        "wires": []
    }
    
    # Criar lista de nós
    nodes = [flow_tab, http_in, function_node, gpio_node, http_response]
    
    # Enviar para Node-RED
    try:
        async with httpx.AsyncClient() as client:
            # Obter flows existentes
            response = await client.get(f"{NODE_RED_URL}/flows")
            existing_flows = response.json()
            
            # Adicionar novos nós
            new_flows = existing_flows + nodes
            
            # Enviar flows atualizados
            response = await client.post(
                f"{NODE_RED_URL}/flows",
                json=new_flows,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 204]:
                print("✅ Flow criado com sucesso!")
                print()
                print("📋 Informações do Flow:")
                print(f"   - Nome: {flow_name}")
                print(f"   - ID: {flow_id}")
                print(f"   - Endpoint: http://<ip-do-pi>:1880/mcp-led")
                print(f"   - GPIO Pin: {gpio_pin}")
                print()
                print("🧪 Teste o endpoint:")
                print(f"   curl -X GET http://localhost:1880/mcp-led")
                print()
                print("🤖 Use com Gemini CLI:")
                print(f"   gemini --mcp mcp://localhost:1880/mcp-led \"acenda o led\"")
                print()
                
                # Salvar configuração em arquivo
                config = {
                    "flow_id": flow_id,
                    "flow_name": flow_name,
                    "endpoint": "/mcp-led",
                    "gpio_pin": gpio_pin,
                    "created_at": datetime.now().isoformat(),
                    "nodes": {
                        "http_in": http_in_id,
                        "function": function_id,
                        "gpio": gpio_id,
                        "response": http_response_id
                    }
                }
                
                with open("led_flow_config.json", "w") as f:
                    json.dump(config, f, indent=2)
                
                print("💾 Configuração salva em: led_flow_config.json")
                
                return True
            else:
                print(f"❌ Erro ao criar flow: {response.status_code}")
                print(response.text)
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def testar_endpoint_mcp():
    """Testa se o endpoint MCP está respondendo"""
    
    print("\n🧪 Testando endpoint MCP...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Testar GET (obter modelo)
            print("1. Testando GET (obter modelo MCP)...")
            response = await client.get("http://localhost:1880/mcp-led")
            
            if response.status_code == 200:
                print("   ✅ Modelo MCP obtido com sucesso!")
                model = response.json()
                print(f"   📦 Funções disponíveis: {[f['name'] for f in model.get('functions', [])]}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
            
            print()
            
            # Testar POST (ligar LED)
            print("2. Testando POST (ligar LED)...")
            response = await client.post(
                "http://localhost:1880/mcp-led",
                json={
                    "function": "setLedState",
                    "arguments": {"state": "on"}
                }
            )
            
            if response.status_code == 200:
                print("   ✅ LED ligado com sucesso!")
                print(f"   📄 Resposta: {response.json()}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
            
            # Aguardar 2 segundos
            await asyncio.sleep(2)
            
            # Testar POST (desligar LED)
            print("\n3. Testando POST (desligar LED)...")
            response = await client.post(
                "http://localhost:1880/mcp-led",
                json={
                    "function": "setLedState",
                    "arguments": {"state": "off"}
                }
            )
            
            if response.status_code == 200:
                print("   ✅ LED desligado com sucesso!")
                print(f"   📄 Resposta: {response.json()}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Erro ao testar: {e}")

async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🔴 GERADOR DE FLOW LED MCP PARA RASPBERRY PI")
    print("=" * 60)
    print()
    
    # Verificar se Node-RED está rodando
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NODE_RED_URL}/flows")
            print(f"✅ Node-RED conectado em {NODE_RED_URL}")
            print()
    except:
        print(f"❌ Node-RED não está rodando em {NODE_RED_URL}")
        print("   Por favor, inicie o Node-RED e tente novamente.")
        return
    
    # Criar flow
    success = await criar_flow_led_mcp_completo(
        gpio_pin=17,
        flow_name="Controle LED via MCP"
    )
    
    if success:
        # Testar endpoint
        resposta = input("\n🧪 Deseja testar o endpoint agora? (s/n): ")
        if resposta.lower() == 's':
            await testar_endpoint_mcp()
    
    print("\n" + "=" * 60)
    print("✅ PROCESSO CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
