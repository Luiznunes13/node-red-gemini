#!/usr/bin/env python3
"""
Servidor MCP para integração com Node-RED
Este servidor fornece ferramentas para criar, gerenciar e executar flows no Node-RED
"""

import asyncio
import json
import logging
import uuid
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
NODE_RED_BASE_URL = "http://192.168.0.36:1880"
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
            name="create_node_red_flow",
            description="Cria um novo flow no Node-RED com configurações especificadas",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_name": {
                        "type": "string",
                        "description": "Nome do flow a ser criado"
                    },
                    "nodes": {
                        "type": "array",
                        "description": "Lista de nós a serem incluídos no flow",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "name": {"type": "string"},
                                "config": {"type": "object"}
                            }
                        }
                    }
                },
                "required": ["flow_name", "nodes"]
            }
        ),
        Tool(
            name="get_node_red_flow",
            description="Obtém informações sobre um flow específico do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_id": {
                        "type": "string",
                        "description": "ID do flow a ser consultado"
                    }
                },
                "required": ["flow_id"]
            }
        ),
        Tool(
            name="update_node_red_flow",
            description="Atualiza um flow existente no Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_id": {
                        "type": "string",
                        "description": "ID do flow a ser atualizado"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Configurações a serem atualizadas no flow"
                    }
                },
                "required": ["flow_id", "updates"]
            }
        ),
        Tool(
            name="delete_node_red_flow",
            description="Remove um flow do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_id": {
                        "type": "string",
                        "description": "ID do flow a ser removido"
                    }
                },
                "required": ["flow_id"]
            }
        ),
        Tool(
            name="deploy_node_red_flows",
            description="Faz o deploy de todos os flows no Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_type": {
                        "type": "string",
                        "enum": ["full", "nodes", "flows"],
                        "description": "Tipo de deployment a ser realizado",
                        "default": "full"
                    }
                }
            }
        ),
        Tool(
            name="get_node_red_nodes",
            description="Lista todos os tipos de nós disponíveis no Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Categoria específica de nós (opcional)"
                    }
                }
            }
        ),
        Tool(
            name="export_node_red_flow",
            description="Exporta um flow do Node-RED para um arquivo JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_id": {
                        "type": "string",
                        "description": "ID do flow a ser exportado"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Caminho para salvar o arquivo exportado"
                    }
                },
                "required": ["flow_id", "file_path"]
            }
        ),
        Tool(
            name="import_node_red_flow",
            description="Importa um flow para o Node-RED a partir de um arquivo JSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Caminho do arquivo JSON a ser importado"
                    },
                    "flow_name": {
                        "type": "string",
                        "description": "Nome para o flow importado (opcional)"
                    }
                },
                "required": ["file_path"]
            }
        ),

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
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Manipula chamadas para as ferramentas do servidor
    """
    try:
        if name == "create_node_red_flow":
            return await create_node_red_flow(arguments)
        elif name == "get_node_red_flow":
            return await get_node_red_flow(arguments)
        elif name == "update_node_red_flow":
            return await update_node_red_flow(arguments)
        elif name == "delete_node_red_flow":
            return await delete_node_red_flow(arguments)
        elif name == "deploy_node_red_flows":
            return await deploy_node_red_flows(arguments)
        elif name == "get_node_red_nodes":
            return await get_node_red_nodes(arguments)
        elif name == "export_node_red_flow":
            return await export_node_red_flow(arguments)
        elif name == "import_node_red_flow":
            return await import_node_red_flow(arguments)

        elif name == "control_gpio_mcp":
            return await control_gpio_mcp(arguments)
        elif name == "control_multiple_gpio_mcp":
            return await control_multiple_gpio_mcp(arguments)
        elif name == "get_gpio_status_mcp":
            return await get_gpio_status_mcp(arguments)
        elif name == "list_mcp_tools":
            return await list_mcp_tools(arguments)
        elif name == "deploy_mcp_gpio_flow":
            return await deploy_mcp_gpio_flow(arguments)
        else:
            raise ValueError(f"Ferramenta desconhecida: {name}")
    
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta {name}: {str(e)}")
        return [TextContent(type="text", text=f"Erro: {str(e)}")]

# Implementação das ferramentas
async def create_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Cria um novo flow no Node-RED"""
    try:
        flow_name = arguments["flow_name"]
        nodes = arguments["nodes"]
        
        # Gerar ID único para o flow
        import uuid
        flow_id = str(uuid.uuid4())
        
        # Criar estrutura do flow
        flow_data = {
            "id": flow_id,
            "label": flow_name,
            "nodes": [],
            "subflows": [],
            "configs": []
        }
        
        # Adicionar nós ao flow
        for i, node in enumerate(nodes):
            node_data = {
                "id": str(uuid.uuid4()),
                "type": node.get("type", "inject"),
                "name": node.get("name", f"Node {i+1}"),
                "x": 100 + (i * 200),  # Posicionamento horizontal
                "y": 100,
                "z": flow_id,
                "wires": [[]]
            }
            
            # Adicionar configurações específicas do nó
            if "config" in node:
                node_data.update(node["config"])
            
            flow_data["nodes"].append(node_data)
        
        # Conectar nós em sequência (opcional)
        for i in range(len(flow_data["nodes"]) - 1):
            current_node = flow_data["nodes"][i]
            next_node = flow_data["nodes"][i + 1]
            current_node["wires"] = [[next_node["id"]]]
        
        # Obter flows existentes
        existing_flows = await node_red_api.get_flows()
        
        # Adicionar novo flow
        existing_flows.append(flow_data)
        
        # Enviar para Node-RED
        result = await node_red_api.post_flows(existing_flows)
        
        return [TextContent(
            type="text",
            text=f"Flow '{flow_name}' criado com sucesso! ID: {flow_id}\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao criar flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao criar flow: {str(e)}"
        )]

async def get_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Obtém informações sobre um flow específico"""
    try:
        flow_id = arguments["flow_id"]
        flow_data = await node_red_api.get_flow(flow_id)
        
        return [TextContent(
            type="text",
            text=f"Informações do Flow ID: {flow_id}\n"
                 f"{json.dumps(flow_data, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao obter flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao obter flow: {str(e)}"
        )]

async def update_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Atualiza um flow existente"""
    try:
        flow_id = arguments["flow_id"]
        updates = arguments["updates"]
        
        # Obter flow atual
        current_flow = await node_red_api.get_flow(flow_id)
        
        # Aplicar atualizações
        current_flow.update(updates)
        
        # Enviar atualização
        result = await node_red_api.put_flow(flow_id, current_flow)
        
        return [TextContent(
            type="text",
            text=f"Flow '{flow_id}' atualizado com sucesso!\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao atualizar flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao atualizar flow: {str(e)}"
        )]

async def delete_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Remove um flow do Node-RED"""
    try:
        flow_id = arguments["flow_id"]
        result = await node_red_api.delete_flow(flow_id)
        
        return [TextContent(
            type="text",
            text=f"Flow '{flow_id}' removido com sucesso!\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao remover flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao remover flow: {str(e)}"
        )]

async def deploy_node_red_flows(arguments: Dict[str, Any]) -> List[TextContent]:
    """Faz deploy dos flows no Node-RED"""
    try:
        deployment_type = arguments.get("deployment_type", "full")
        
        # Obter flows atuais
        flows = await node_red_api.get_flows()
        
        # Fazer deploy
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{node_red_api.base_url}/flows",
                json=flows,
                headers={**node_red_api.headers, "Node-RED-Deployment-Type": deployment_type}
            )
            response.raise_for_status()
            result = response.json()
        
        return [TextContent(
            type="text",
            text=f"Deploy realizado com sucesso! Tipo: {deployment_type}\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao fazer deploy: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao fazer deploy: {str(e)}"
        )]

async def get_node_red_nodes(arguments: Dict[str, Any]) -> List[TextContent]:
    """Lista todos os tipos de nós disponíveis"""
    try:
        nodes_data = await node_red_api.get_nodes()
        
        category = arguments.get("category")
        if category:
            # Filtrar por categoria se especificada
            filtered_nodes = [
                node for node in nodes_data 
                if node.get("category", "").lower() == category.lower()
            ]
            nodes_data = filtered_nodes
        
        return [TextContent(
            type="text",
            text=f"Nós disponíveis no Node-RED:\n"
                 f"{json.dumps(nodes_data, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao obter nós: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao obter nós: {str(e)}"
        )]

async def export_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Exporta um flow para arquivo JSON"""
    try:
        flow_id = arguments["flow_id"]
        file_path = arguments["file_path"]
        
        # Obter flow
        flow_data = await node_red_api.get_flow(flow_id)
        
        # Salvar em arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, indent=2, ensure_ascii=False)
        
        return [TextContent(
            type="text",
            text=f"Flow '{flow_id}' exportado com sucesso para: {file_path}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao exportar flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao exportar flow: {str(e)}"
        )]

async def import_node_red_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Importa um flow de arquivo JSON"""
    try:
        file_path = arguments["file_path"]
        flow_name = arguments.get("flow_name")
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        # Atualizar nome se fornecido
        if flow_name:
            flow_data["label"] = flow_name
        
        # Gerar novo ID se necessário
        if "id" not in flow_data:
            import uuid
            flow_data["id"] = str(uuid.uuid4())
        
        # Obter flows existentes
        existing_flows = await node_red_api.get_flows()
        
        # Adicionar flow importado
        existing_flows.append(flow_data)
        
        # Enviar para Node-RED
        result = await node_red_api.post_flows(existing_flows)
        
        return [TextContent(
            type="text",
            text=f"Flow importado com sucesso de: {file_path}\n"
                 f"ID: {flow_data['id']}\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao importar flow: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao importar flow: {str(e)}"
        )]



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