#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar a discrepância entre dados do banco e sistema
O banco retorna 0 alunos, mas o sistema carrega 315 alunos
"""

import os
from datetime import datetime

print("🔍 INVESTIGAÇÃO: DISCREPÂNCIA DE DADOS")
print("=" * 60)
print(f"Data/Hora: {datetime.now()}")

# 1. Verificar conexão direta com MongoDB usando diferentes métodos
print("\n🔗 1. TESTANDO DIFERENTES MÉTODOS DE ACESSO AO BANCO:")

# Método 1: Usando AlunoDAO diretamente
print("\n📋 Método 1: AlunoDAO.listar_todos()")
try:
    from models import AlunoDAO
    alunos_dao = AlunoDAO.listar_todos()
    print(f"   Resultado: {len(alunos_dao) if alunos_dao else 0} alunos")
    if alunos_dao and len(alunos_dao) > 0:
        print(f"   Primeiro aluno: {alunos_dao[0].get('nome', 'N/A')}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Método 2: Usando conexão direta do MongoDB
print("\n📋 Método 2: Conexão direta MongoDB")
try:
    from database_integration_robusto import DatabaseIntegration
    db_integration = DatabaseIntegration()
    
    if db_integration.db:
        collection = db_integration.db.alunos
        count = collection.count_documents({})
        print(f"   Total documentos na collection 'alunos': {count}")
        
        if count > 0:
            # Buscar alguns documentos
            docs = list(collection.find().limit(5))
            print(f"   Primeiros 5 documentos:")
            for i, doc in enumerate(docs, 1):
                nome = doc.get('nome', 'N/A')
                print(f"      {i}. {nome}")
    else:
        print("   ❌ Conexão com banco não estabelecida")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Método 3: Verificar todas as collections
print("\n📋 Método 3: Listar todas as collections")
try:
    from database_integration_robusto import DatabaseIntegration
    db_integration = DatabaseIntegration()
    
    if db_integration.db:
        collections = db_integration.db.list_collection_names()
        print(f"   Collections disponíveis: {collections}")
        
        for collection_name in collections:
            if 'aluno' in collection_name.lower():
                collection = db_integration.db[collection_name]
                count = collection.count_documents({})
                print(f"   Collection '{collection_name}': {count} documentos")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Verificar como o sistema carrega os dados
print("\n🏫 2. INVESTIGANDO CARREGAMENTO DO SISTEMA:")
try:
    # Importar o sistema
    from app import academia
    
    if academia:
        print(f"   ✅ Sistema inicializado")
        print(f"   Tipo do objeto academia: {type(academia)}")
        
        # Verificar atributos disponíveis
        attrs = [attr for attr in dir(academia) if not attr.startswith('_')]
        print(f"   Atributos disponíveis: {attrs[:10]}...")  # Primeiros 10
        
        # Verificar dados de alunos
        if hasattr(academia, 'alunos_reais'):
            alunos = academia.alunos_reais
            print(f"   ✅ alunos_reais: {len(alunos)} alunos")
            
            if len(alunos) > 0:
                print(f"   Primeiro aluno: {alunos[0]}")
                print(f"   Último aluno: {alunos[-1]}")
                
                # Verificar se os alunos da imagem estão nos dados carregados
                alunos_imagem = [
                    "JOÃO VITOR GOMES SANTOS",
                    "KELVIN ENRIQUE DA SILVA DA SILVA", 
                    "HENRY DE SOUZA VERAS",
                    "ANA CLARA SILVA SANTOS",
                    "CARLOS EDUARDO SOUZA"
                ]
                
                print(f"\n   🔍 Verificando primeiros 5 alunos da imagem:")
                nomes_sistema = [aluno.get('nome', '').upper() for aluno in alunos]
                
                for nome in alunos_imagem:
                    if nome.upper() in nomes_sistema:
                        print(f"      ✅ {nome} - ENCONTRADO")
                        # Buscar dados completos
                        for aluno in alunos:
                            if aluno.get('nome', '').upper() == nome.upper():
                                print(f"         Atividade: {aluno.get('atividade', 'N/A')}")
                                print(f"         Turma: {aluno.get('turma', 'N/A')}")
                                print(f"         Status: {aluno.get('ativo', 'N/A')}")
                                break
                    else:
                        print(f"      ❌ {nome} - NÃO ENCONTRADO")
        else:
            print(f"   ❌ Atributo 'alunos_reais' não encontrado")
    else:
        print(f"   ❌ Sistema não inicializado")
        
except Exception as e:
    print(f"   ❌ Erro ao acessar sistema: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar se há problemas na inicialização dos DAOs
print("\n🔧 3. VERIFICANDO INICIALIZAÇÃO DOS DAOs:")
try:
    from models import AlunoDAO, AtividadeDAO, TurmaDAO
    
    print(f"   AlunoDAO: {type(AlunoDAO)}")
    print(f"   AtividadeDAO: {type(AtividadeDAO)}")
    print(f"   TurmaDAO: {type(TurmaDAO)}")
    
    # Verificar se os DAOs têm conexão com banco
    if hasattr(AlunoDAO, 'collection'):
        print(f"   AlunoDAO.collection: {AlunoDAO.collection}")
    if hasattr(AlunoDAO, 'db'):
        print(f"   AlunoDAO.db: {AlunoDAO.db}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 60)
print("🎯 INVESTIGAÇÃO CONCLUÍDA")
print("\n💡 POSSÍVEIS CAUSAS DA DISCREPÂNCIA:")
print("   1. AlunoDAO não está conectado corretamente ao banco")
print("   2. Sistema está usando dados em cache/memória")
print("   3. Problema na inicialização dos DAOs")
print("   4. Dados estão em collection diferente")
print("   5. Problema de permissões no banco")