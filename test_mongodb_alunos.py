#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import init_mongodb, AlunoDAO, AtividadeDAO
import sys

print("🔍 Testando conexão MongoDB e dados dos alunos...")

# Inicializar MongoDB
db = init_mongodb()

try:
    print("\n📊 Verificando dados dos alunos...")
    
    # Listar todos os alunos
    alunos = AlunoDAO.listar_todos()
    print(f"Total de alunos encontrados: {len(alunos)}")
    
    if len(alunos) > 0:
        print("\n👥 Primeiros 5 alunos:")
        for i, aluno in enumerate(alunos[:5]):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   ID: {aluno.get('_id', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print(f"   Ativo: {aluno.get('ativo', 'N/A')}")
            print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
            print()
    
    # Verificar atividades
    print("\n🎯 Verificando atividades...")
    atividades = AtividadeDAO.listar_todas()
    print(f"Total de atividades: {len(atividades)}")
    
    if len(atividades) > 0:
        print("\n📋 Atividades disponíveis:")
        for ativ in atividades:
            print(f"- Nome: {ativ.get('nome', 'N/A')} (ID: {ativ.get('_id', 'N/A')})")
    
    # Verificar quantos alunos têm atividade preenchida
    alunos_com_atividade = 0
    alunos_sem_atividade = 0
    
    for aluno in alunos:
        if aluno.get('atividade') and aluno.get('atividade').strip():
            alunos_com_atividade += 1
        else:
            alunos_sem_atividade += 1
    
    print(f"\n📊 Estatísticas:")
    print(f"Alunos com atividade: {alunos_com_atividade}")
    print(f"Alunos sem atividade: {alunos_sem_atividade}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Teste concluído!")