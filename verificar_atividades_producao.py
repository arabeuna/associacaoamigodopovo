#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from models import init_mongodb, AlunoDAO, AtividadeDAO
import sys
from collections import Counter

print("🔍 Verificando atividades dos alunos no AMBIENTE DE PRODUÇÃO...")

# Carregar variáveis de ambiente de produção
load_dotenv('.env.production')
print(f"📍 Usando banco: {os.getenv('MONGO_DATABASE')}")
print(f"📍 Cluster: {os.getenv('MONGO_CLUSTER')}")

# Inicializar MongoDB com configurações de produção
db = init_mongodb()

try:
    print("\n📊 Analisando dados dos alunos no ambiente de produção...")
    
    # Listar todos os alunos
    alunos = AlunoDAO.listar_todos()
    print(f"Total de alunos encontrados: {len(alunos)}")
    
    # Contar atividades
    atividades_count = Counter()
    alunos_sem_atividade = 0
    alunos_com_atividade_vazia = 0
    
    print("\n📋 Primeiros 10 alunos e suas atividades:")
    for i, aluno in enumerate(alunos[:10]):
        nome = aluno.get('nome', 'N/A')
        atividade = aluno.get('atividade', '')
        atividades_ids = aluno.get('atividades_ids', [])
        
        print(f"{i+1}. {nome}")
        print(f"   - Atividade: '{atividade}'")
        print(f"   - Atividades IDs: {atividades_ids}")
        print()
    
    # Contar todas as atividades
    for aluno in alunos:
        atividade = aluno.get('atividade', '')
        
        if not atividade:
            alunos_sem_atividade += 1
        elif atividade.strip() == '':
            alunos_com_atividade_vazia += 1
        else:
            atividades_count[atividade] += 1
    
    print(f"\n📊 Distribuição de atividades:")
    for atividade, count in atividades_count.most_common():
        print(f"- {atividade}: {count} alunos")
    
    print(f"\n⚠️  Problemas encontrados:")
    print(f"- Alunos sem campo 'atividade': {alunos_sem_atividade}")
    print(f"- Alunos com atividade vazia: {alunos_com_atividade_vazia}")
    
    # Verificar se há alunos com atividades_ids mas sem atividade
    alunos_com_ids_sem_nome = 0
    for aluno in alunos:
        atividade = aluno.get('atividade', '')
        atividades_ids = aluno.get('atividades_ids', [])
        
        if atividades_ids and not atividade.strip():
            alunos_com_ids_sem_nome += 1
    
    print(f"- Alunos com atividades_ids mas sem nome da atividade: {alunos_com_ids_sem_nome}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Verificação concluída!")