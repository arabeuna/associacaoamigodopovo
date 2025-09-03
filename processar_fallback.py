#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar registros pendentes do fallback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_integration_robusto import DatabaseIntegrationRobusto

def main():
    print("🔄 Iniciando processamento de registros pendentes do fallback...")
    
    # Criar instância do sistema robusto
    db_robusto = DatabaseIntegrationRobusto()
    
    # Processar registros pendentes
    resultado = db_robusto.processar_fallback_pendente()
    
    print(f"\n📊 Resultado do processamento:")
    print(f"   - Registros processados: {resultado.get('processed', 0)}")
    
    if 'message' in resultado:
        print(f"   - Mensagem: {resultado['message']}")
    
    if 'errors' in resultado and resultado['errors']:
        print(f"   - Erros encontrados: {len(resultado['errors'])}")
        for error in resultado['errors']:
            print(f"     • {error}")
    
    if 'remaining' in resultado:
        print(f"   - Registros ainda pendentes: {resultado['remaining']}")
    
    print("\n✅ Processamento concluído!")

if __name__ == '__main__':
    main()