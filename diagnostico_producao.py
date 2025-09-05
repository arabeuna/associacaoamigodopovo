#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo para ambiente de produção
Verifica conexão MongoDB, carregamento de dados e inicialização do sistema
"""

import os
import sys
from datetime import datetime

print("🔍 DIAGNÓSTICO COMPLETO - AMBIENTE DE PRODUÇÃO")
print("=" * 60)
print(f"Data/Hora: {datetime.now()}")
print(f"Python: {sys.version}")
print(f"Diretório: {os.getcwd()}")

# 1. Verificar variáveis de ambiente
print("\n📋 1. VERIFICANDO VARIÁVEIS DE AMBIENTE:")
env_vars = [
    'MONGO_URI', 'MONGO_USERNAME', 'MONGO_PASSWORD', 
    'MONGO_CLUSTER', 'MONGO_DATABASE', 'FLASK_ENV'
]

for var in env_vars:
    value = os.environ.get(var, 'NÃO DEFINIDA')
    if 'PASSWORD' in var or 'URI' in var:
        # Mascarar dados sensíveis
        if value != 'NÃO DEFINIDA':
            masked = value[:10] + '***' + value[-10:] if len(value) > 20 else '***'
            print(f"   {var}: {masked}")
        else:
            print(f"   {var}: {value}")
    else:
        print(f"   {var}: {value}")

# 2. Testar conexão MongoDB direta
print("\n🔗 2. TESTANDO CONEXÃO MONGODB ATLAS:")
try:
    from pymongo import MongoClient
    
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print("❌ MONGO_URI não definida")
    else:
        print("✅ MONGO_URI encontrada")
        
        # Testar conexão
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ Ping MongoDB: SUCESSO")
        
        # Testar banco
        db_name = os.environ.get('MONGO_DATABASE', 'amigodopovoassociacao_db')
        db = client[db_name]
        
        # Contar documentos
        alunos_count = db.alunos.count_documents({})
        print(f"✅ Alunos no banco: {alunos_count}")
        
        if alunos_count > 0:
            # Mostrar amostra
            sample = list(db.alunos.find({}, {'nome': 1, 'atividade': 1}).limit(3))
            print("📋 Amostra de alunos:")
            for i, aluno in enumerate(sample, 1):
                nome = aluno.get('nome', 'N/A')
                atividade = aluno.get('atividade', 'N/A')
                print(f"   {i}. {nome} - {atividade}")
        
        client.close()
        
except Exception as e:
    print(f"❌ Erro na conexão MongoDB: {e}")

# 3. Testar inicialização do sistema
print("\n🚀 3. TESTANDO INICIALIZAÇÃO DO SISTEMA:")
try:
    # Importar models primeiro
    from models import init_mongodb, AlunoDAO, USE_MEMORY_FALLBACK
    
    print(f"✅ Models importados")
    print(f"   Modo fallback: {USE_MEMORY_FALLBACK}")
    
    # Testar DAO
    alunos = AlunoDAO.listar_todos()
    print(f"✅ AlunoDAO.listar_todos(): {len(alunos)} alunos")
    
    if len(alunos) == 0:
        print("⚠️ PROBLEMA: Nenhum aluno retornado pelo DAO")
        print("   Possíveis causas:")
        print("   - Sistema usando fallback em memória")
        print("   - Conexão MongoDB falhando silenciosamente")
        print("   - Coleção 'alunos' vazia no banco")
    
except Exception as e:
    print(f"❌ Erro ao importar/testar sistema: {e}")
    import traceback
    traceback.print_exc()

# 4. Testar inicialização da classe Academia
print("\n🏫 4. TESTANDO CLASSE ACADEMIA:")
try:
    from app import SistemaAcademia
    
    print("✅ Importando SistemaAcademia...")
    academia_test = SistemaAcademia()
    
    print(f"✅ Academia inicializada")
    print(f"   Alunos carregados: {len(academia_test.alunos_reais)}")
    
    if len(academia_test.alunos_reais) == 0:
        print("❌ PROBLEMA CRÍTICO: Academia não carregou alunos")
        print("   Verificar método carregar_dados_reais()")
    else:
        print("✅ Academia funcionando corretamente")
        
except Exception as e:
    print(f"❌ Erro ao inicializar Academia: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎯 DIAGNÓSTICO CONCLUÍDO")
print("\n💡 PRÓXIMOS PASSOS:")
print("1. Se MongoDB conecta mas Academia não carrega dados:")
print("   - Verificar método carregar_dados_reais()")
print("   - Verificar se get_db_integration() funciona")
print("2. Se está usando fallback em memória:")
print("   - Verificar inicialização do MongoDB")
print("   - Verificar variáveis de ambiente no Render")
print("3. Se nenhum dado aparece:")
print("   - Problema na inicialização da aplicação Flask")