#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação específica dos alunos da imagem no banco MongoDB
Para entender exatamente quais estão presentes e quais não estão
"""

import os
from datetime import datetime

print("🔍 VERIFICAÇÃO ESPECÍFICA: ALUNOS DA IMAGEM")
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

print(f"\n📋 VERIFICANDO {len(alunos_imagem)} ALUNOS DA IMAGEM NO BANCO:")

try:
    from database_integration_robusto import DatabaseIntegrationRobusto
    
    db_integration = DatabaseIntegrationRobusto()
    
    if db_integration.db is not None:
        collection = db_integration.db.alunos
        total_banco = collection.count_documents({})
        print(f"\n✅ Conectado ao MongoDB - Total de alunos no banco: {total_banco}")
        
        encontrados = []
        nao_encontrados = []
        
        print(f"\n🔍 VERIFICAÇÃO DETALHADA:")
        print("=" * 60)
        
        for i, nome_imagem in enumerate(alunos_imagem, 1):
            print(f"\n{i:2d}. {nome_imagem}")
            
            # Busca exata (case-insensitive)
            doc = collection.find_one({"nome": {"$regex": f"^{nome_imagem}$", "$options": "i"}})
            
            if doc:
                encontrados.append(nome_imagem)
                ativo = doc.get('ativo', True)
                status_str = "✅ ATIVO" if ativo else "⚠️ INATIVO"
                print(f"    ✅ ENCONTRADO NO BANCO - {status_str}")
                print(f"    📋 Atividade: {doc.get('atividade', 'N/A')}")
                print(f"    🏫 Turma: {doc.get('turma', 'N/A')}")
                print(f"    📅 Data Cadastro: {doc.get('data_cadastro', 'N/A')}")
                print(f"    📧 Email: {doc.get('email', 'N/A')}")
                print(f"    📞 Telefone: {doc.get('telefone', 'N/A')}")
            else:
                nao_encontrados.append(nome_imagem)
                print(f"    ❌ NÃO ENCONTRADO NO BANCO")
                
                # Tentar busca parcial para ver se há nomes similares
                palavras = nome_imagem.split()
                if len(palavras) >= 2:
                    primeiro_nome = palavras[0]
                    ultimo_nome = palavras[-1]
                    
                    # Buscar por primeiro e último nome
                    similar = list(collection.find({
                        "$and": [
                            {"nome": {"$regex": primeiro_nome, "$options": "i"}},
                            {"nome": {"$regex": ultimo_nome, "$options": "i"}}
                        ]
                    }).limit(3))
                    
                    if similar:
                        print(f"    🔍 Nomes similares encontrados:")
                        for sim in similar:
                            print(f"       - {sim.get('nome', 'N/A')}")
        
        print(f"\n" + "=" * 60)
        print(f"📊 RESUMO FINAL:")
        print(f"   ✅ Encontrados no banco: {len(encontrados)}/{len(alunos_imagem)}")
        print(f"   ❌ Não encontrados: {len(nao_encontrados)}")
        
        if encontrados:
            print(f"\n✅ ALUNOS ENCONTRADOS NO BANCO ({len(encontrados)}):")
            for nome in encontrados:
                print(f"   • {nome}")
        
        if nao_encontrados:
            print(f"\n❌ ALUNOS NÃO ENCONTRADOS NO BANCO ({len(nao_encontrados)}):")
            for nome in nao_encontrados:
                print(f"   • {nome}")
        
        # Verificar se há problemas de dados
        print(f"\n🔍 ANÁLISE ADICIONAL:")
        
        # Contar alunos inativos
        inativos = collection.count_documents({"ativo": False})
        print(f"   ⚠️ Total de alunos inativos no banco: {inativos}")
        
        # Contar alunos sem atividade definida
        sem_atividade = collection.count_documents({
            "$or": [
                {"atividade": {"$exists": False}},
                {"atividade": ""},
                {"atividade": None},
                {"atividade": "Cadastro Geral"}
            ]
        })
        print(f"   📋 Alunos com atividade genérica/indefinida: {sem_atividade}")
        
        # Contar alunos sem turma definida
        sem_turma = collection.count_documents({
            "$or": [
                {"turma": {"$exists": False}},
                {"turma": ""},
                {"turma": None},
                {"turma": "A definir"}
            ]
        })
        print(f"   🏫 Alunos com turma indefinida: {sem_turma}")
        
    else:
        print("❌ Não foi possível conectar ao MongoDB")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 60)
print("🎯 VERIFICAÇÃO CONCLUÍDA")
print("\n💡 CONCLUSÃO:")
print("   Se os alunos estão no banco mas não aparecem no dashboard,")
print("   o problema é provavelmente na interface (filtros, paginação, cache)")
print("   ou na consulta do frontend.")