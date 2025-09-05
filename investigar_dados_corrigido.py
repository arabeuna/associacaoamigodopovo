#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script corrigido para investigar os dados dos alunos
Usando a classe correta DatabaseIntegrationRobusto
"""

import os
from datetime import datetime

print("🔍 INVESTIGAÇÃO CORRIGIDA: DADOS DOS ALUNOS")
print("=" * 60)
print(f"Data/Hora: {datetime.now()}")

# Lista de alunos da imagem fornecida pelo usuário
alunos_imagem = [
    "JOÃO VITOR GOMES SANTOS",
    "KELVIN ENRIQUE DA SILVA DA SILVA", 
    "HENRY DE SOUZA VERAS",
    "ANA CLARA SILVA SANTOS",
    "CARLOS EDUARDO SOUZA",
    "MARIANA COSTA RIBEIRO",
    "PEDRO HENRIQUE DIAS",
    "LARISSA OLIVEIRA MELO",
    "DIEGO FERREIRA LIMA",
    "REGINA SANTOS BARBOSA",
    "ROBERTO SILVA MENDES",
    "ALEXANDRE COSTA MOURA",
    "PATRICIA SANTOS ROCHA",
    "LETÍCIA FERREIRA GOMES",
    "RAFAEL SANTOS OLIVEIRA",
    "MIGUEL SANTOS COSTA",
    "HELENA OLIVEIRA SILVA",
    "CAIO SANTOS FERREIRA"
]

print(f"\n📋 ALUNOS DA IMAGEM ({len(alunos_imagem)} alunos):")
for i, nome in enumerate(alunos_imagem, 1):
    print(f"   {i:2d}. {nome}")

# 1. Verificar dados usando DatabaseIntegrationRobusto
print("\n🔗 1. VERIFICANDO DADOS USANDO DatabaseIntegrationRobusto:")
try:
    from database_integration_robusto import DatabaseIntegrationRobusto
    
    db_integration = DatabaseIntegrationRobusto()
    
    # Verificar se tem conexão com banco
    if db_integration.db:
        print("   ✅ Conexão com MongoDB estabelecida")
        
        # Acessar collection de alunos diretamente
        collection = db_integration.db.alunos
        count = collection.count_documents({})
        print(f"   📊 Total de documentos na collection 'alunos': {count}")
        
        if count > 0:
            # Buscar alguns documentos
            docs = list(collection.find().limit(10))
            print(f"\n   📋 Primeiros 10 alunos no banco:")
            for i, doc in enumerate(docs, 1):
                nome = doc.get('nome', 'N/A')
                atividade = doc.get('atividade', 'N/A')
                print(f"      {i:2d}. {nome} - {atividade}")
            
            # Verificar se os alunos da imagem estão no banco
            print(f"\n   🔍 VERIFICANDO ALUNOS DA IMAGEM NO BANCO:")
            nomes_banco = [doc.get('nome', '').upper() for doc in collection.find()]
            
            encontrados_banco = []
            nao_encontrados_banco = []
            
            for nome_imagem in alunos_imagem:
                if nome_imagem.upper() in nomes_banco:
                    encontrados_banco.append(nome_imagem)
                    print(f"      ✅ {nome_imagem} - ENCONTRADO NO BANCO")
                    
                    # Buscar dados completos
                    doc = collection.find_one({"nome": {"$regex": f"^{nome_imagem}$", "$options": "i"}})
                    if doc:
                        print(f"         Atividade: {doc.get('atividade', 'N/A')}")
                        print(f"         Turma: {doc.get('turma', 'N/A')}")
                        print(f"         Data Cadastro: {doc.get('data_cadastro', 'N/A')}")
                        print(f"         Status Ativo: {doc.get('ativo', 'N/A')}")
                else:
                    nao_encontrados_banco.append(nome_imagem)
                    print(f"      ❌ {nome_imagem} - NÃO ENCONTRADO NO BANCO")
            
            print(f"\n   📊 RESUMO BANCO:")
            print(f"      Encontrados: {len(encontrados_banco)}/{len(alunos_imagem)}")
            print(f"      Não encontrados: {len(nao_encontrados_banco)}")
        
    else:
        print("   ⚠️ Sem conexão com MongoDB - usando modo fallback")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# 2. Verificar dados carregados no sistema
print("\n🏫 2. VERIFICANDO DADOS CARREGADOS NO SISTEMA:")
try:
    from app import academia
    
    if academia and hasattr(academia, 'alunos_reais'):
        alunos_sistema = academia.alunos_reais
        print(f"   ✅ Total de alunos no sistema: {len(alunos_sistema)}")
        
        if len(alunos_sistema) > 0:
            print(f"\n   📋 Primeiros 10 alunos no sistema:")
            for i, aluno in enumerate(alunos_sistema[:10], 1):
                nome = aluno.get('nome', 'N/A')
                atividade = aluno.get('atividade', 'N/A')
                print(f"      {i:2d}. {nome} - {atividade}")
            
            # Verificar se os alunos da imagem estão no sistema
            print(f"\n   🔍 VERIFICANDO ALUNOS DA IMAGEM NO SISTEMA:")
            nomes_sistema = [aluno.get('nome', '').upper() for aluno in alunos_sistema]
            
            encontrados_sistema = []
            nao_encontrados_sistema = []
            
            for nome_imagem in alunos_imagem:
                if nome_imagem.upper() in nomes_sistema:
                    encontrados_sistema.append(nome_imagem)
                    print(f"      ✅ {nome_imagem} - ENCONTRADO NO SISTEMA")
                    
                    # Buscar dados completos
                    for aluno in alunos_sistema:
                        if aluno.get('nome', '').upper() == nome_imagem.upper():
                            print(f"         Atividade: {aluno.get('atividade', 'N/A')}")
                            print(f"         Turma: {aluno.get('turma', 'N/A')}")
                            print(f"         Status Ativo: {aluno.get('ativo', 'N/A')}")
                            break
                else:
                    nao_encontrados_sistema.append(nome_imagem)
                    print(f"      ❌ {nome_imagem} - NÃO ENCONTRADO NO SISTEMA")
            
            print(f"\n   📊 RESUMO SISTEMA:")
            print(f"      Encontrados: {len(encontrados_sistema)}/{len(alunos_imagem)}")
            print(f"      Não encontrados: {len(nao_encontrados_sistema)}")
        
    else:
        print(f"   ❌ Sistema não inicializado ou sem dados")
        
except Exception as e:
    print(f"   ❌ Erro ao acessar sistema: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar se há filtros ou problemas na interface
print("\n🔍 3. ANÁLISE DE POSSÍVEIS PROBLEMAS NA INTERFACE:")
print("\n💡 POSSÍVEIS CAUSAS DOS ALUNOS NÃO APARECEREM NO DASHBOARD:")
print("   1. 🔍 Filtros ativos na interface (por atividade, turma, status)")
print("   2. 📊 Paginação - alunos podem estar em outras páginas")
print("   3. 🔤 Problemas de busca/ordenação")
print("   4. ⚙️ Cache do navegador ou dados desatualizados")
print("   5. 🎯 Campos obrigatórios em branco (atividade, turma)")
print("   6. 📱 Problemas de renderização no frontend")
print("   7. 🔒 Status 'ativo' definido como False")

print("\n🔧 SOLUÇÕES RECOMENDADAS:")
print("   1. ✅ Verificar se há filtros ativos na interface")
print("   2. 🔄 Limpar cache do navegador e recarregar página")
print("   3. 🔍 Testar busca específica por nome")
print("   4. 📊 Verificar se há paginação ativa")
print("   5. ⚙️ Verificar logs do sistema em tempo real")
print("   6. 🎯 Testar com dados de exemplo")

print("\n" + "=" * 60)
print("🎯 INVESTIGAÇÃO CONCLUÍDA")