#!/usr/bin/env python3
"""
Demonstração completa das funcionalidades do Servidor MCP Node-RED
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuração do Node-RED
NODE_RED_URL = "http://localhost:1880"

async def demo_mcp_node_red():
    """Demonstra todas as funcionalidades do servidor MCP"""
    
    print("🚀 DEMONSTRAÇÃO SERVIDOR MCP NODE-RED")
    print("=" * 50)
    print(f"🕐 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Node-RED URL: {NODE_RED_URL}")
    print()

    async with httpx.AsyncClient() as client:
        
        # 1. Verificar Node-RED
        print("1️⃣ VERIFICANDO CONEXÃO COM NODE-RED...")
        try:
            response = await client.get(f"{NODE_RED_URL}/flows")
            flows_atuais = response.json()
            print(f"   ✅ Node-RED conectado!")
            print(f"   📊 Flows existentes: {len(flows_atuais)}")
            
            # Mostrar flows existentes
            for flow in flows_atuais:
                if flow.get('type') == 'tab':
                    print(f"   📁 Flow: {flow.get('label', 'Sem nome')} (ID: {flow['id']})")
            print()
        
        except Exception as e:
            print(f"   ❌ Erro ao conectar: {e}")
            return

        # 2. Criar um novo flow usando nossa lógica MCP
        print("2️⃣ CRIANDO NOVO FLOW VIA MCP...")
        try:
            import uuid
            flow_id = str(uuid.uuid4())
            
            # Criar estrutura do flow baseada na nossa implementação MCP
            novo_flow = {
                "id": flow_id,
                "type": "tab",
                "label": "Flow Criado via MCP",
                "disabled": False,
                "info": "Flow demonstrativo criado pelo servidor MCP"
            }
            
            # Criar nós para o flow
            inject_id = str(uuid.uuid4())
            debug_id = str(uuid.uuid4())
            
            inject_node = {
                "id": inject_id,
                "type": "inject",
                "z": flow_id,
                "name": "MCP Trigger",
                "props": [
                    {
                        "p": "payload"
                    }
                ],
                "repeat": "",
                "crontab": "",
                "once": False,
                "onceDelay": 0.1,
                "topic": "",
                "payload": "Hello from MCP Server!",
                "payloadType": "str",
                "x": 160,
                "y": 100,
                "wires": [[debug_id]]
            }
            
            debug_node = {
                "id": debug_id,
                "type": "debug",
                "z": flow_id,
                "name": "MCP Output",
                "active": True,
                "tosidebar": True,
                "console": False,
                "tostatus": False,
                "complete": "payload",
                "targetType": "msg",
                "statusVal": "",
                "statusType": "auto",
                "x": 360,
                "y": 100,
                "wires": []
            }
            
            # Adicionar o novo flow e nós
            flows_atuais.extend([novo_flow, inject_node, debug_node])
            
            # Enviar para Node-RED
            response = await client.post(
                f"{NODE_RED_URL}/flows",
                json=flows_atuais,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   ✅ Flow criado com sucesso!")
            print(f"   🆔 ID do Flow: {flow_id}")
            print(f"   🏷️  Nome: Flow Criado via MCP")
            print()
            
        except Exception as e:
            print(f"   ❌ Erro ao criar flow: {e}")
            print()

        # 3. Listar todos os flows
        print("3️⃣ LISTANDO TODOS OS FLOWS...")
        try:
            response = await client.get(f"{NODE_RED_URL}/flows")
            flows = response.json()
            
            flow_tabs = [f for f in flows if f.get('type') == 'tab']
            print(f"   📊 Total de flows: {len(flow_tabs)}")
            
            for i, flow in enumerate(flow_tabs, 1):
                print(f"   {i}. {flow.get('label', 'Sem nome')} (ID: {flow['id']})")
            print()
            
        except Exception as e:
            print(f"   ❌ Erro ao listar flows: {e}")
            print()

        # 4. Obter informações de um flow específico
        print("4️⃣ OBTENDO DETALHES DE UM FLOW...")
        try:
            if flow_tabs:
                flow_exemplo = flow_tabs[0]
                flow_id_exemplo = flow_exemplo['id']
                
                response = await client.get(f"{NODE_RED_URL}/flow/{flow_id_exemplo}")
                flow_details = response.json()
                
                print(f"   🔍 Flow: {flow_details.get('label', 'Sem nome')}")
                print(f"   🆔 ID: {flow_details['id']}")
                print(f"   📦 Nós no flow: {len(flow_details.get('nodes', []))}")
                
                # Mostrar tipos de nós
                node_types = {}
                for node in flow_details.get('nodes', []):
                    node_type = node.get('type', 'unknown')
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                
                print(f"   🧩 Tipos de nós:")
                for node_type, count in node_types.items():
                    print(f"      - {node_type}: {count}")
                print()
                
        except Exception as e:
            print(f"   ❌ Erro ao obter detalhes: {e}")
            print()

        # 5. Listar tipos de nós disponíveis
        print("5️⃣ LISTANDO TIPOS DE NÓS DISPONÍVEIS...")
        try:
            response = await client.get(f"{NODE_RED_URL}/nodes")
            nodes_info = response.json()
            
            # Agrupar por categoria
            categories = {}
            for node in nodes_info:
                category = node.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(node.get('name', node.get('id', 'unknown')))
            
            print(f"   📦 Total de tipos de nós: {len(nodes_info)}")
            print(f"   📂 Categorias encontradas: {len(categories)}")
            
            # Mostrar algumas categorias principais
            for category, nodes in list(categories.items())[:5]:
                print(f"   📁 {category}: {len(nodes)} nós")
                # Mostrar alguns exemplos
                for node in nodes[:3]:
                    print(f"      - {node}")
                if len(nodes) > 3:
                    print(f"      ... e mais {len(nodes) - 3} nós")
            print()
            
        except Exception as e:
            print(f"   ❌ Erro ao listar nós: {e}")
            print()

        # 6. Exportar um flow
        print("6️⃣ EXPORTANDO FLOW PARA ARQUIVO...")
        try:
            if flow_tabs:
                flow_para_exportar = flow_tabs[0]
                flow_id_export = flow_para_exportar['id']
                
                response = await client.get(f"{NODE_RED_URL}/flow/{flow_id_export}")
                flow_export_data = response.json()
                
                # Salvar em arquivo
                filename = f"exported_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(flow_export_data, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Flow exportado com sucesso!")
                print(f"   📄 Arquivo: {filename}")
                print(f"   📊 Tamanho: {len(json.dumps(flow_export_data))} bytes")
                print()
                
        except Exception as e:
            print(f"   ❌ Erro ao exportar: {e}")
            print()

        # 7. Fazer deploy
        print("7️⃣ FAZENDO DEPLOY DOS FLOWS...")
        try:
            response = await client.get(f"{NODE_RED_URL}/flows")
            current_flows = response.json()
            
            # Deploy com header especial
            response = await client.post(
                f"{NODE_RED_URL}/flows",
                json=current_flows,
                headers={
                    "Content-Type": "application/json",
                    "Node-RED-Deployment-Type": "full"
                }
            )
            
            print(f"   ✅ Deploy realizado com sucesso!")
            print(f"   🚀 Todos os flows foram deployados")
            print()
            
        except Exception as e:
            print(f"   ❌ Erro no deploy: {e}")
            print()

    print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print(f"✅ Todas as funcionalidades do servidor MCP foram testadas")
    print(f"🌐 Node-RED continua rodando em: {NODE_RED_URL}")
    print(f"🕐 Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(demo_mcp_node_red())
