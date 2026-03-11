#!/usr/bin/env python3
"""
Servidor MCP para integração com Node-RED
Este servidor fornece ferramentas para criar, gerenciar e executar flows no Node-RED
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-node-red")

# Instância do servidor MCP
server = Server("mcp-node-red")

# Configurações padrão do Node-RED
NODE_RED_BASE_URL = "http://192.168.0.44:1880"
NODE_RED_ADMIN_AUTH = None  # Pode ser configurado se necessário

class NodeRedAPI:
    """Cliente para interagir com a API REST do Node-RED"""
    
    def __init__(self, base_url: str = NODE_RED_BASE_URL, auth: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.headers = {"Content-Type": "application/json"}
        if auth:
            self.headers["Authorization"] = f"Bearer {auth}"
    
    async def get_flows(self) -> Dict[str, Any]:
        """Obtém todos os flows do Node-RED"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/flows", headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def post_flows(self, flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Envia flows para o Node-RED"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/flows", 
                json=flows, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_flow(self, flow_id: str) -> Dict[str, Any]:
        """Obtém um flow específico"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/flow/{flow_id}", 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def put_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um flow específico"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/flow/{flow_id}", 
                json=flow_data, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_flow(self, flow_id: str) -> Dict[str, Any]:
        """Remove um flow específico"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/flow/{flow_id}", 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Obtém todos os tipos de nós disponíveis"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/nodes", headers=self.headers)
            response.raise_for_status()
            return response.json()

# Instância da API do Node-RED
node_red_api = NodeRedAPI()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    Lista todas as ferramentas disponíveis no servidor MCP
    """
    return [
        Tool(
            name="control_gpio_mcp",
            description="Controla GPIO individual via API MCP do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "description": "Número do pino GPIO (2-27 BCM)",
                        "minimum": 2,
                        "maximum": 27
                    },
                    "state": {
                        "type": "string",
                        "enum": ["on", "off", "true", "false", "1", "0"],
                        "description": "Estado desejado do GPIO"
                    }
                },
                "required": ["pin", "state"]
            }
        ),
        Tool(
            name="control_multiple_gpio_mcp",
            description="Controla múltiplas GPIOs simultaneamente via API MCP do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "gpios": {
                        "type": "array",
                        "description": "Lista de GPIOs para controlar",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pin": {
                                    "type": "integer",
                                    "minimum": 2,
                                    "maximum": 27
                                },
                                "state": {
                                    "type": "string",
                                    "enum": ["on", "off", "true", "false", "1", "0"]
                                }
                            },
                            "required": ["pin", "state"]
                        }
                    }
                },
                "required": ["gpios"]
            }
        ),
        Tool(
            name="get_gpio_status_mcp",
            description="Obtém status atual de todas as GPIOs via API MCP do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_mcp_tools",
            description="Lista todas as ferramentas MCP disponíveis no Node-RED",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="deploy_mcp_gpio_flow",
            description="Implanta o flow MCP GPIO completo no Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "node_red_url": {
                        "type": "string",
                        "description": "URL do Node-RED",
                        "default": "http://localhost:1880"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_dht_sensor_mcp",
            description="Obtém a leitura atual de temperatura e umidade do sensor DHT11 via Node-RED",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="set_sensor_alert",
            description=(
                "Configura limiares de alerta para o sensor DHT11. "
                "Quando a temperatura ou umidade cruzar o limiar configurado, o alerta é armazenado "
                "e pode ser consultado com get_sensor_alerts para tomar ação (ex: ligar ventilador)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "temp_above": {
                        "type": "number",
                        "description": "Disparar alerta se temperatura SUBIR acima deste valor (°C)"
                    },
                    "temp_below": {
                        "type": "number",
                        "description": "Disparar alerta se temperatura CAIR abaixo deste valor (°C)"
                    },
                    "humidity_above": {
                        "type": "number",
                        "description": "Disparar alerta se umidade SUBIR acima deste valor (%)"
                    },
                    "humidity_below": {
                        "type": "number",
                        "description": "Disparar alerta se umidade CAIR abaixo deste valor (%)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_sensor_alerts",
            description=(
                "Retorna todos os alertas do sensor DHT11 que foram disparados desde a última consulta. "
                "Use esta ferramenta para verificar se algum limiar foi cruzado e depois tome a ação adequada "
                "(ex: ligar ventilador com control_gpio_mcp, notificar usuário, etc)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "clear_after_read": {
                        "type": "boolean",
                        "description": "Se true, limpa a fila após leitura (padrão: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="clear_sensor_alerts",
            description="Limpa toda a fila de alertas pendentes do sensor DHT11.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="set_action_plan",
            description=(
                "Cria ou atualiza um plano de ação autônomo baseado em sensor. "
                "O Node-RED executa a ação GPIO automaticamente a cada leitura do DHT11 (30s), "
                "sem precisar do Gemini ativo. Registre também o raciocínio no campo 'description'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "trigger": {
                        "type": "string",
                        "enum": ["temp_above", "temp_below", "humidity_above", "humidity_below"],
                        "description": "Condição que dispara a ação"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Valor do limiar (°C para temperatura, % para umidade)"
                    },
                    "pin": {
                        "type": "integer",
                        "description": "Pino GPIO do ESP8266 a ser acionado"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["on", "off"],
                        "description": "Ação a executar: ligar ou desligar o pino"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição do objetivo deste plano (ex: 'ligar ventilador quando quente')"
                    },
                    "id": {
                        "type": "string",
                        "description": "ID único do plano (para atualizar um existente). Omitir para criar novo."
                    }
                },
                "required": ["trigger", "threshold", "pin", "action"]
            }
        ),
        Tool(
            name="list_action_plans",
            description="Lista todos os planos de ação autônomos ativos no Node-RED.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="delete_action_plan",
            description="Remove um plano de ação autônomo pelo ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID do plano a remover (obtido com list_action_plans)"
                    }
                },
                "required": ["id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Manipula chamadas para as ferramentas do servidor
    """
    try:
        if name == "control_gpio_mcp":
            return await control_gpio_mcp(arguments)
        elif name == "control_multiple_gpio_mcp":
            return await control_multiple_gpio_mcp(arguments)
        elif name == "get_gpio_status_mcp":
            return await get_gpio_status_mcp(arguments)
        elif name == "list_mcp_tools":
            return await list_mcp_tools(arguments)
        elif name == "deploy_mcp_gpio_flow":
            return await deploy_mcp_gpio_flow(arguments)
        elif name == "get_dht_sensor_mcp":
            return await get_dht_sensor_mcp(arguments)
        elif name == "set_sensor_alert":
            return await set_sensor_alert(arguments)
        elif name == "get_sensor_alerts":
            return await get_sensor_alerts(arguments)
        elif name == "clear_sensor_alerts":
            return await clear_sensor_alerts(arguments)
        elif name == "set_action_plan":
            return await set_action_plan(arguments)
        elif name == "list_action_plans":
            return await list_action_plans(arguments)
        elif name == "delete_action_plan":
            return await delete_action_plan(arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {name}: {str(e)}")
        return [TextContent(type="text", text=f"Erro: {str(e)}")]

async def control_gpio_mcp(arguments: Dict[str, Any]) -> List[TextContent]:
    """Controla GPIO individual via API MCP do Node-RED"""
    try:
        pin = arguments["pin"]
        state = arguments["state"]
        
        # Dados para a requisição MCP
        mcp_data = {
            "tool": "control_gpio",
            "params": {
                "pin": pin,
                "state": state
            }
        }
        
        # Fazer requisição para o endpoint MCP do Node-RED
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/mcp/gpio/control",
                json=mcp_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        return [TextContent(
            type="text",
            text=f"GPIO {pin} controlada com sucesso!\n"
                 f"Estado: {state}\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao controlar GPIO: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao controlar GPIO: {str(e)}"
        )]

async def control_multiple_gpio_mcp(arguments: Dict[str, Any]) -> List[TextContent]:
    """Controla múltiplas GPIOs simultaneamente via API MCP do Node-RED"""
    try:
        gpios = arguments["gpios"]
        
        # Dados para a requisição MCP
        mcp_data = {
            "tool": "control_multiple_gpio",
            "params": {
                "gpios": gpios
            }
        }
        
        # Fazer requisição para o endpoint MCP do Node-RED
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/mcp/gpio/control",
                json=mcp_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        return [TextContent(
            type="text",
            text=f"Múltiplas GPIOs controladas com sucesso!\n"
                 f"Total: {len(gpios)} GPIOs\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao controlar múltiplas GPIOs: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao controlar múltiplas GPIOs: {str(e)}"
        )]

async def get_gpio_status_mcp(arguments: Dict[str, Any]) -> List[TextContent]:
    """Obtém status atual de todas as GPIOs via API MCP do Node-RED"""
    try:
        # Fazer requisição para o endpoint de status
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{node_red_api.base_url}/mcp/gpio/status",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        # Extrair informações relevantes
        gpio_info = result.get("result", {})
        available_pins = gpio_info.get("available_pins", [])
        active_pins = gpio_info.get("active_pins", [])
        states = gpio_info.get("states", {})
        
        status_text = f"Status das GPIOs:\n"
        status_text += f"• Pinos disponíveis: {len(available_pins)} ({', '.join(map(str, available_pins))})\n"
        status_text += f"• Pinos ativos: {len(active_pins)} ({', '.join(map(str, active_pins))})\n"
        status_text += f"• Modo: {gpio_info.get('pin_mode', 'BCM')}\n\n"
        
        if states:
            status_text += "Estados atuais:\n"
            for pin, state_info in states.items():
                status_text += f"  GPIO {pin}: {state_info.get('state', 'unknown')} "
                status_text += f"(valor: {state_info.get('value', 'N/A')}) "
                status_text += f"- {state_info.get('timestamp', 'N/A')}\n"
        else:
            status_text += "Nenhuma GPIO ativa no momento.\n"
        
        status_text += f"\nDados completos: {json.dumps(result, indent=2)}"
        
        return [TextContent(
            type="text",
            text=status_text
        )]
        
    except Exception as e:
        logger.error(f"Erro ao obter status das GPIOs: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao obter status das GPIOs: {str(e)}"
        )]

async def list_mcp_tools(arguments: Dict[str, Any]) -> List[TextContent]:
    """Lista todas as ferramentas MCP disponíveis no Node-RED"""
    try:
        # Fazer requisição para o endpoint de ferramentas
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{node_red_api.base_url}/mcp/tools",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        tools = result.get("tools", [])
        
        tools_text = f"Ferramentas MCP disponíveis no Node-RED ({len(tools)} total):\n\n"
        
        for i, tool in enumerate(tools, 1):
            name = tool.get("name", "N/A")
            description = tool.get("description", "N/A")
            parameters = tool.get("parameters", {})
            
            tools_text += f"{i}. {name}\n"
            tools_text += f"   Descrição: {description}\n"
            
            if parameters:
                tools_text += f"   Parâmetros:\n"
                for param_name, param_info in parameters.items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "N/A")
                    required = " (obrigatório)" if param_info.get("required") else ""
                    tools_text += f"     • {param_name} ({param_type}){required}: {param_desc}\n"
            
            tools_text += "\n"
        
        tools_text += f"Dados completos: {json.dumps(result, indent=2)}"
        
        return [TextContent(
            type="text",
            text=tools_text
        )]
        
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas MCP: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao listar ferramentas MCP: {str(e)}"
        )]

async def deploy_mcp_gpio_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Implanta o flow MCP GPIO completo no Node-RED"""
    try:
        node_red_url = arguments.get("node_red_url", "http://localhost:1880")
        
        # Carregar o flow MCP GPIO do arquivo
        flow_file = Path(__file__).parent / "flows_mcp_gpio_completo.json"
        
        if not flow_file.exists():
            return [TextContent(
                type="text",
                text=f"❌ Arquivo de flow não encontrado: {flow_file}\n"
                     f"Execute primeiro o script 'deploy_mcp_gpio_flow.py' para criar o arquivo."
            )]
        
        with open(flow_file, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        # Fazer backup dos flows existentes
        async with httpx.AsyncClient() as client:
            backup_response = await client.get(f"{node_red_url}/flows")
            
            if backup_response.status_code == 200:
                backup_file = Path(__file__).parent / "flows_backup.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_response.json(), f, indent=2, ensure_ascii=False)
        
        # Obter flows existentes e adicionar o novo
        existing_flows = backup_response.json() if backup_response.status_code == 200 else []
        updated_flows = existing_flows + flow_data
        
        # Deploy do flow atualizado
        async with httpx.AsyncClient() as client:
            deploy_response = await client.post(
                f"{node_red_url}/flows",
                json=updated_flows,
                headers={'Content-Type': 'application/json'}
            )
            deploy_response.raise_for_status()
        
        # Testar endpoints após deploy
        await asyncio.sleep(2)  # Aguardar processamento
        
        test_results = []
        
        # Teste 1: Listar ferramentas
        try:
            async with httpx.AsyncClient() as client:
                tools_response = await client.get(f"{node_red_url}/mcp/tools")
                if tools_response.status_code == 200:
                    tools = tools_response.json()
                    test_results.append(f"✅ GET /mcp/tools - {len(tools.get('tools', []))} ferramentas")
                else:
                    test_results.append(f"❌ GET /mcp/tools - Status: {tools_response.status_code}")
        except Exception as e:
            test_results.append(f"❌ GET /mcp/tools - Erro: {e}")
        
        # Teste 2: Status das GPIOs
        try:
            async with httpx.AsyncClient() as client:
                status_response = await client.get(f"{node_red_url}/mcp/gpio/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    pins_available = len(status.get('result', {}).get('available_pins', []))
                    test_results.append(f"✅ GET /mcp/gpio/status - {pins_available} pinos disponíveis")
                else:
                    test_results.append(f"❌ GET /mcp/gpio/status - Status: {status_response.status_code}")
        except Exception as e:
            test_results.append(f"❌ GET /mcp/gpio/status - Erro: {e}")
        
        success_text = f"🎉 Flow MCP GPIO implantado com sucesso!\n\n"
        success_text += f"🔧 Endpoints disponíveis:\n"
        success_text += f"   • POST {node_red_url}/mcp/gpio/control\n"
        success_text += f"   • GET  {node_red_url}/mcp/gpio/status\n"
        success_text += f"   • GET  {node_red_url}/mcp/tools\n\n"
        success_text += f"🧪 Testes dos endpoints:\n"
        success_text += "\n".join(test_results)
        success_text += f"\n\n📚 Exemplos de uso:\n"
        success_text += f"# Ligar GPIO 20\n"
        success_text += f'curl -X POST {node_red_url}/mcp/gpio/control \\\n'
        success_text += f'  -H "Content-Type: application/json" \\\n'
        success_text += f'  -d \'{{"tool": "control_gpio", "params": {{"pin": 20, "state": "on"}}}}\'\n\n'
        success_text += f"# Controlar múltiplas GPIOs\n"
        success_text += f'curl -X POST {node_red_url}/mcp/gpio/control \\\n'
        success_text += f'  -H "Content-Type: application/json" \\\n'
        success_text += f'  -d \'{{"tool": "control_multiple_gpio", "params": {{"gpios": [{{"pin": 20, "state": "on"}}, {{"pin": 21, "state": "off"}}]}}}}\''
        
        return [TextContent(
            type="text",
            text=success_text
        )]
        
    except Exception as e:
        logger.error(f"Erro ao implantar flow MCP GPIO: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao implantar flow MCP GPIO: {str(e)}"
        )]

async def get_dht_sensor_mcp(arguments: Dict[str, Any]) -> List[TextContent]:
    """Obtém leitura de temperatura e umidade do sensor DHT11"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{node_red_api.base_url}/mcp/sensor/dht",
                headers={"Content-Type": "application/json"}
            )
            result = response.json()

        if response.status_code == 503:
            return [TextContent(type="text", text=f"Sensor DHT11 ainda sem dados. {result.get('error', '')}")]

        data = result.get("result", {})
        text = (
            f"Leitura do sensor DHT11:\n"
            f"  Temperatura : {data.get('temperature', 'N/A')} °C\n"
            f"  Umidade     : {data.get('humidity', 'N/A')} %\n"
            f"  Device      : {data.get('device_id', 'N/A')}\n"
            f"  Atualizado  : {data.get('timestamp', 'N/A')}"
        )
        return [TextContent(type="text", text=text)]

    except Exception as e:
        logger.error(f"Erro ao ler DHT sensor: {str(e)}")
        return [TextContent(type="text", text=f"Erro ao ler sensor DHT11: {str(e)}")]


async def set_sensor_alert(arguments: Dict[str, Any]) -> List[TextContent]:
    """Configura limiares de alerta para o sensor DHT11"""
    try:
        config = {}
        if "temp_above" in arguments:
            config["temp_above"] = float(arguments["temp_above"])
        if "temp_below" in arguments:
            config["temp_below"] = float(arguments["temp_below"])
        if "humidity_above" in arguments:
            config["humidity_above"] = float(arguments["humidity_above"])
        if "humidity_below" in arguments:
            config["humidity_below"] = float(arguments["humidity_below"])

        if not config:
            return [TextContent(type="text", text="Nenhum limiar informado. Informe pelo menos um: temp_above, temp_below, humidity_above ou humidity_below.")]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/mcp/sensor/alerts/config",
                json=config,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

        saved = result.get("config", config)
        lines = ["Alertas configurados com sucesso! O sensor será monitorado a cada leitura (~30s).\n"]
        lines.append("Limiares ativos:")
        if "temp_above"    in saved: lines.append(f"  • Temperatura ACIMA de {saved['temp_above']} °C")
        if "temp_below"    in saved: lines.append(f"  • Temperatura ABAIXO de {saved['temp_below']} °C")
        if "humidity_above" in saved: lines.append(f"  • Umidade ACIMA de {saved['humidity_above']} %")
        if "humidity_below" in saved: lines.append(f"  • Umidade ABAIXO de {saved['humidity_below']} %")
        lines.append("\nUse get_sensor_alerts() para verificar se algum alerta foi disparado.")
        return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        logger.error(f"Erro ao configurar alertas: {str(e)}")
        return [TextContent(type="text", text=f"Erro ao configurar alertas: {str(e)}")]


async def get_sensor_alerts(arguments: Dict[str, Any]) -> List[TextContent]:
    """Retorna alertas disparados do sensor DHT11"""
    try:
        clear = arguments.get("clear_after_read", True)

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{node_red_api.base_url}/mcp/sensor/alerts")
            response.raise_for_status()
            result = response.json()

        alerts = result.get("alerts", [])
        config = result.get("config", {})

        if not alerts:
            cfg_lines = []
            if config:
                if "temp_above"    in config: cfg_lines.append(f"temperatura > {config['temp_above']} °C")
                if "temp_below"    in config: cfg_lines.append(f"temperatura < {config['temp_below']} °C")
                if "humidity_above" in config: cfg_lines.append(f"umidade > {config['humidity_above']} %")
                if "humidity_below" in config: cfg_lines.append(f"umidade < {config['humidity_below']} %")
                return [TextContent(type="text", text=f"Nenhum alerta pendente.\nMonitorando: {', '.join(cfg_lines)}")]
            return [TextContent(type="text", text="Nenhum alerta pendente e nenhum limiar configurado. Use set_sensor_alert() primeiro.")]

        lines = [f"ALERTA: {len(alerts)} alerta(s) disparado(s)!\n"]
        for a in alerts:
            tipo = "Temperatura" if a["type"] == "temperature" else "Umidade"
            unidade = "°C" if a["type"] == "temperature" else "%"
            lines.append(f"  [{a['timestamp']}] {tipo} {a['condition']} do limiar {a['threshold']}{unidade} → valor: {a['value']}{unidade}")

        lines.append("\nAção sugerida: use control_gpio_mcp() para ligar/desligar dispositivos conforme necessário.")

        if clear:
            async with httpx.AsyncClient() as client:
                await client.post(f"{node_red_api.base_url}/mcp/sensor/alerts/clear")
            lines.append("(Fila limpa após leitura)")

        return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        logger.error(f"Erro ao ler alertas: {str(e)}")
        return [TextContent(type="text", text=f"Erro ao ler alertas: {str(e)}")]


async def clear_sensor_alerts(arguments: Dict[str, Any]) -> List[TextContent]:
    """Limpa a fila de alertas pendentes do sensor DHT11"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{node_red_api.base_url}/mcp/sensor/alerts/clear")
            response.raise_for_status()
        return [TextContent(type="text", text="Fila de alertas limpa com sucesso.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro ao limpar alertas: {str(e)}")]


async def set_action_plan(arguments: Dict[str, Any]) -> List[TextContent]:
    """Cria ou atualiza um plano de ação autônomo baseado em sensor"""
    try:
        payload = {
            "trigger":     arguments["trigger"],
            "threshold":   float(arguments["threshold"]),
            "pin":         int(arguments["pin"]),
            "action":      arguments["action"],
            "description": arguments.get("description", ""),
        }
        if "id" in arguments:
            payload["id"] = arguments["id"]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/mcp/action/plan",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

        plan = result.get("plan", payload)
        trigger_label = {
            "temp_above":     f"temperatura SUBIR acima de {plan['threshold']} °C",
            "temp_below":     f"temperatura CAIR abaixo de {plan['threshold']} °C",
            "humidity_above": f"umidade SUBIR acima de {plan['threshold']} %",
            "humidity_below": f"umidade CAIR abaixo de {plan['threshold']} %",
        }.get(plan["trigger"], plan["trigger"])

        lines = [
            f"Plano de ação criado! ID: {plan['id']}",
            f"",
            f"Regra: quando {trigger_label}",
            f"Ação:  pino {plan['pin']} → {plan['action'].upper()}",
            f"Descrição: {plan.get('description') or '—'}",
            f"",
            f"O Node-RED executará esta ação automaticamente a cada leitura do sensor (~30s).",
            f"Use list_action_plans() para ver todos os planos ativos.",
        ]
        return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        logger.error(f"Erro ao criar plano: {str(e)}")
        return [TextContent(type="text", text=f"Erro ao criar plano de ação: {str(e)}")]


async def list_action_plans(arguments: Dict[str, Any]) -> List[TextContent]:
    """Lista planos de ação autônomos ativos"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{node_red_api.base_url}/mcp/action/plans")
            response.raise_for_status()
            result = response.json()

        plans = result.get("plans", [])
        if not plans:
            return [TextContent(type="text", text="Nenhum plano de ação configurado. Use set_action_plan() para criar um.")]

        trigger_labels = {
            "temp_above":     "temperatura >",
            "temp_below":     "temperatura <",
            "humidity_above": "umidade >",
            "humidity_below": "umidade <",
        }
        lines = [f"Planos de ação ativos ({len(plans)} total):\n"]
        for p in plans:
            status = "ativo" if p.get("active", True) else "inativo"
            label = trigger_labels.get(p["trigger"], p["trigger"])
            unidade = "°C" if "temp" in p["trigger"] else "%"
            lines.append(f"  [{p['id']}] {status.upper()}")
            lines.append(f"    Regra: {label} {p['threshold']}{unidade} → pino {p['pin']} {p['action'].upper()}")
            if p.get("description"):
                lines.append(f"    Descrição: {p['description']}")
            lines.append("")
        return [TextContent(type="text", text="\n".join(lines))]

    except Exception as e:
        return [TextContent(type="text", text=f"Erro ao listar planos: {str(e)}")]


async def delete_action_plan(arguments: Dict[str, Any]) -> List[TextContent]:
    """Remove um plano de ação autônomo pelo ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/mcp/action/plan/delete",
                json={"id": arguments["id"]},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        return [TextContent(type="text", text=f"Plano '{arguments['id']}' removido com sucesso.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro ao remover plano: {str(e)}")]


# Função principal para executar o servidor
async def main():
    """Função principal para executar o servidor MCP"""
    logger.info("Iniciando servidor MCP para Node-RED...")
    
    # Executar servidor via stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())