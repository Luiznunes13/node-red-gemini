#!/usr/bin/env python3
"""
Teste de validação do main.py
"""

import sys
sys.path.insert(0, 'C:\\Users\\44057824820\\Documents\\Projetos_pos\\mcp-node-red')

try:
    import main
    print("✅ main.py importado com sucesso!")
    print(f"✅ Servidor definido: {main.server}")
    print(f"✅ API Node-RED: {main.node_red_api}")
    print("\n🎉 Todas as validações passaram!")
except Exception as e:
    print(f"❌ Erro ao importar: {e}")
    import traceback
    traceback.print_exc()
