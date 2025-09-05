#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import init_mongodb, AlunoDAO
import sys

print("🔍 Buscando aluno 'teste teste teste'...")

# Inicializar MongoDB
db = init_mongodb()

try:
    print("\n📊 Verificando dados dos alunos...")
    
    # Listar todos os alunos
    alunos = AlunoDAO.listar_todos()
    print(f"Total de alunos encontrados: {len(alunos)}")
    
    # Buscar especificamente por 'teste teste teste'
    aluno_teste = None
    alunos_teste = []
    
    for aluno in alunos:
        nome = aluno.get('nome', '').lower()
        if 'teste' in nome:
            alunos_teste.append(aluno)
            if nome == 'teste teste teste':
                aluno_teste = aluno
    
    print(f"\n🎯 Alunos com 'teste' no nome: {len(alunos_teste)}")
    
    if alunos_teste:
        print("\n📋 Alunos encontrados com 'teste':")
        for i, aluno in enumerate(alunos_teste):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   ID: {aluno.get('_id', 'N/A')}")
            print(f"   Telefone: {aluno.get('telefone', 'N/A')}")
            print(f"   Email: {aluno.get('email', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print(f"   Ativo: {aluno.get('ativo', 'N/A')}")
            print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
            print(f"   Criado em: {aluno.get('criado_em', 'N/A')}")
            print()
    
    if aluno_teste:
        print("✅ ENCONTRADO: Aluno 'teste teste teste' está no banco de dados!")
        print(f"   ID: {aluno_teste.get('_id')}")
        print(f"   Data de cadastro: {aluno_teste.get('data_cadastro')}")
        print(f"   Criado em: {aluno_teste.get('criado_em')}")
    else:
        print("❌ NÃO ENCONTRADO: Aluno 'teste teste teste' não foi encontrado no banco.")
    
    # Verificar também os últimos alunos cadastrados
    print("\n📅 Últimos 10 alunos cadastrados:")
    alunos_ordenados = sorted(alunos, key=lambda x: x.get('criado_em', ''), reverse=True)
    
    for i, aluno in enumerate(alunos_ordenados[:10]):
        print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
        print(f"   Criado em: {aluno.get('criado_em', 'N/A')}")
        print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
        print()
    
except Exception as e:
    print(f"❌ Erro ao verificar dados: {e}")
    sys.exit(1)

print("\n✅ Verificação concluída!")