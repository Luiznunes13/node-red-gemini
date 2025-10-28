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
NODE_RED_BASE_URL = "http://localhost:1880"
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
            name="control_raspberry_pi_led",
            description="Controla um LED conectado ao Raspberry Pi via GPIO através do Node-RED",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["on", "off"],
                        "description": "Estado desejado do LED (on para ligar, off para desligar)"
                    },
                    "gpio_pin": {
                        "type": "integer",
                        "description": "Número do pino GPIO (opcional, padrão: 17)",
                        "default": 17
                    }
                },
                "required": ["state"]
            }
        ),
        Tool(
            name="create_raspberry_pi_led_flow",
            description="Cria um flow completo no Node-RED para controlar LED via GPIO no Raspberry Pi",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_name": {
                        "type": "string",
                        "description": "Nome do flow para controle de LED",
                        "default": "Controle LED Raspberry Pi"
                    },
                    "gpio_pin": {
                        "type": "integer",
                        "description": "Número do pino GPIO",
                        "default": 17
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
        elif name == "control_raspberry_pi_led":
            return await control_raspberry_pi_led(arguments)
        elif name == "create_raspberry_pi_led_flow":
            return await create_raspberry_pi_led_flow(arguments)
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

async def control_raspberry_pi_led(arguments: Dict[str, Any]) -> List[TextContent]:
    """Controla um LED conectado ao Raspberry Pi via GPIO através do Node-RED"""
    try:
        state = arguments["state"]
        gpio_pin = arguments.get("gpio_pin", 17)
        
        # Criar flow para controle do LED
        flow_data = {
            "id": str(uuid.uuid4()),
            "label": "Controle LED Raspberry Pi",
            "nodes": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "rpi-gpio out",
                    "name": "LED",
                    "pin": gpio_pin,
                    "state": state,
                    "wires": []
                }
            ],
            "subflows": [],
            "configs": []
        }
        
        # Obter flows existentes
        existing_flows = await node_red_api.get_flows()
        
        # Adicionar novo flow
        existing_flows.append(flow_data)
        
        # Enviar para Node-RED
        result = await node_red_api.post_flows(existing_flows)
        
        return [TextContent(
            type="text",
            text=f"Flow de controle de LED criado com sucesso!\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao criar flow de controle de LED: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao criar flow de controle de LED: {str(e)}"
        )]

async def create_raspberry_pi_led_flow(arguments: Dict[str, Any]) -> List[TextContent]:
    """Cria um flow completo no Node-RED para controlar LED via GPIO no Raspberry Pi"""
    try:
        flow_name = arguments.get("flow_name", "Controle LED Raspberry Pi")
        gpio_pin = arguments.get("gpio_pin", 17)
        
        # Gerar ID único para o flow
        import uuid
        flow_id = str(uuid.uuid4())
        
        # Criar estrutura do flow
        flow_data = {
            "id": flow_id,
            "label": flow_name,
            "nodes": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "rpi-gpio out",
                    "name": "LED",
                    "pin": gpio_pin,
                    "state": "off",
                    "wires": []
                }
            ],
            "subflows": [],
            "configs": []
        }
        
        # Obter flows existentes
        existing_flows = await node_red_api.get_flows()
        
        # Adicionar novo flow
        existing_flows.append(flow_data)
        
        # Enviar para Node-RED
        result = await node_red_api.post_flows(existing_flows)
        
        return [TextContent(
            type="text",
            text=f"Flow completo para controle de LED criado com sucesso!\n"
                 f"Resultado: {json.dumps(result, indent=2)}"
        )]
        
    except Exception as e:
        logger.error(f"Erro ao criar flow completo de controle de LED: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Erro ao criar flow completo de controle de LED: {str(e)}"
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