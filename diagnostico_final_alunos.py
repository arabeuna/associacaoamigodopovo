#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico final: Por que alguns alunos não aparecem no dashboard
Script corrigido para verificar adequadamente os dados
"""

import os
from datetime import datetime

print("🔍 DIAGNÓSTICO FINAL: ALUNOS AUSENTES NO DASHBOARD")
print("=" * 70)
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

# 1. Verificar dados usando conexão direta com MongoDB
print("\n🔗 1. VERIFICANDO DADOS DIRETAMENTE NO MONGODB:")
try:
    from database_integration_robusto import DatabaseIntegrationRobusto
    
    db_integration = DatabaseIntegrationRobusto()
    
    # Verificar se tem conexão com banco (comparar com None)
    if db_integration.db is not None:
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
                ativo = doc.get('ativo', 'N/A')
                print(f"      {i:2d}. {nome} - {atividade} - Ativo: {ativo}")
            
            # Verificar se os alunos da imagem estão no banco
            print(f"\n   🔍 VERIFICANDO ALUNOS DA IMAGEM NO BANCO:")
            
            encontrados_banco = 0
            nao_encontrados_banco = 0
            
            for nome_imagem in alunos_imagem:
                # Busca case-insensitive
                doc = collection.find_one({"nome": {"$regex": f"^{nome_imagem}$", "$options": "i"}})
                if doc:
                    encontrados_banco += 1
                    ativo = doc.get('ativo', True)  # Default True se não especificado
                    status_str = "✅ ATIVO" if ativo else "⚠️ INATIVO"
                    print(f"      ✅ {nome_imagem} - ENCONTRADO - {status_str}")
                    print(f"         Atividade: {doc.get('atividade', 'N/A')}")
                    print(f"         Turma: {doc.get('turma', 'N/A')}")
                    print(f"         Data Cadastro: {doc.get('data_cadastro', 'N/A')}")
                else:
                    nao_encontrados_banco += 1
                    print(f"      ❌ {nome_imagem} - NÃO ENCONTRADO NO BANCO")
            
            print(f"\n   📊 RESUMO BANCO:")
            print(f"      Encontrados: {encontrados_banco}/{len(alunos_imagem)}")
            print(f"      Não encontrados: {nao_encontrados_banco}")
            
            # Verificar se há alunos inativos
            inativos = collection.count_documents({"ativo": False})
            print(f"      Alunos inativos no banco: {inativos}")
        
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
    
    if academia is not None and hasattr(academia, 'alunos_reais'):
        alunos_sistema = academia.alunos_reais
        print(f"   ✅ Total de alunos no sistema: {len(alunos_sistema)}")
        
        if len(alunos_sistema) > 0:
            print(f"\n   📋 Primeiros 10 alunos no sistema:")
            for i, aluno in enumerate(alunos_sistema[:10], 1):
                nome = aluno.get('nome', 'N/A')
                atividade = aluno.get('atividade', 'N/A')
                ativo = aluno.get('ativo', True)
                status_str = "✅ ATIVO" if ativo else "⚠️ INATIVO"
                print(f"      {i:2d}. {nome} - {atividade} - {status_str}")
            
            # Verificar se os alunos da imagem estão no sistema
            print(f"\n   🔍 VERIFICANDO ALUNOS DA IMAGEM NO SISTEMA:")
            
            encontrados_sistema = 0
            nao_encontrados_sistema = 0
            alunos_inativos_sistema = 0
            
            for nome_imagem in alunos_imagem:
                encontrado = False
                for aluno in alunos_sistema:
                    if aluno.get('nome', '').upper() == nome_imagem.upper():
                        encontrado = True
                        encontrados_sistema += 1
                        ativo = aluno.get('ativo', True)
                        if not ativo:
                            alunos_inativos_sistema += 1
                        status_str = "✅ ATIVO" if ativo else "⚠️ INATIVO"
                        print(f"      ✅ {nome_imagem} - ENCONTRADO - {status_str}")
                        print(f"         Atividade: {aluno.get('atividade', 'N/A')}")
                        print(f"         Turma: {aluno.get('turma', 'N/A')}")
                        break
                
                if not encontrado:
                    nao_encontrados_sistema += 1
                    print(f"      ❌ {nome_imagem} - NÃO ENCONTRADO NO SISTEMA")
            
            print(f"\n   📊 RESUMO SISTEMA:")
            print(f"      Encontrados: {encontrados_sistema}/{len(alunos_imagem)}")
            print(f"      Não encontrados: {nao_encontrados_sistema}")
            print(f"      Alunos inativos encontrados: {alunos_inativos_sistema}")
        
    else:
        print(f"   ❌ Sistema não inicializado ou sem dados")
        
except Exception as e:
    print(f"   ❌ Erro ao acessar sistema: {e}")
    import traceback
    traceback.print_exc()

# 3. Análise final e recomendações
print("\n🎯 3. ANÁLISE FINAL E DIAGNÓSTICO:")
print("\n🔍 POSSÍVEIS CAUSAS DOS ALUNOS NÃO APARECEREM:")
print("\n   📊 PROBLEMAS DE DADOS:")
print("      • Alunos com status 'ativo' = False")
print("      • Campos obrigatórios em branco (atividade, turma)")
print("      • Dados inconsistentes entre banco e sistema")
print("\n   🖥️ PROBLEMAS DE INTERFACE:")
print("      • Filtros ativos no dashboard (por atividade, turma, status)")
print("      • Paginação - alunos em outras páginas")
print("      • Cache do navegador desatualizado")
print("      • Problemas de busca/ordenação")
print("\n   ⚙️ PROBLEMAS TÉCNICOS:")
print("      • Problemas na consulta/renderização do frontend")
print("      • Sincronização entre banco e sistema")
print("      • Logs de erro não capturados")

print("\n🔧 SOLUÇÕES RECOMENDADAS:")
print("\n   1. ✅ VERIFICAÇÕES IMEDIATAS:")
print("      • Limpar todos os filtros na interface")
print("      • Verificar se há paginação ativa")
print("      • Limpar cache do navegador (Ctrl+F5)")
print("      • Testar busca específica por nome")
print("\n   2. 🔧 CORREÇÕES DE DADOS:")
print("      • Verificar e corrigir status 'ativo' dos alunos")
print("      • Preencher campos obrigatórios em branco")
print("      • Sincronizar dados entre banco e sistema")
print("\n   3. 🔍 INVESTIGAÇÃO ADICIONAL:")
print("      • Verificar logs do sistema em tempo real")
print("      • Testar com dados de exemplo")
print("      • Verificar permissões de acesso aos dados")

print("\n" + "=" * 70)
print("🎯 DIAGNÓSTICO CONCLUÍDO")
print("\n💡 PRÓXIMO PASSO: Verificar filtros ativos na interface do dashboard")