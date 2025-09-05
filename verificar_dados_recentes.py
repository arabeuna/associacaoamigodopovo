#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import init_mongodb, AlunoDAO
from datetime import datetime, date
import sys

print("🔍 Verificando dados recentes no banco de produção...")

# Inicializar MongoDB
db = init_mongodb()

try:
    print("\n📊 Verificando dados dos alunos...")
    
    # Listar todos os alunos
    alunos = AlunoDAO.listar_todos()
    print(f"Total de alunos encontrados: {len(alunos)}")
    
    # Data de hoje
    hoje = date.today()
    print(f"Data de hoje: {hoje}")
    
    # Buscar alunos cadastrados hoje
    alunos_hoje = []
    alunos_teste = []
    
    for aluno in alunos:
        nome = aluno.get('nome', '').lower()
        data_cadastro = aluno.get('data_cadastro')
        
        # Verificar se contém 'teste' no nome
        if 'teste' in nome:
            alunos_teste.append(aluno)
        
        # Verificar se foi cadastrado hoje
        if data_cadastro:
            try:
                if isinstance(data_cadastro, str):
                    # Tentar diferentes formatos de data
                    data_obj = None
                    formatos = ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
                    for formato in formatos:
                        try:
                            data_obj = datetime.strptime(data_cadastro, formato).date()
                            break
                        except:
                            continue
                    
                    if data_obj and data_obj == hoje:
                        alunos_hoje.append(aluno)
                elif hasattr(data_cadastro, 'date'):
                    if data_cadastro.date() == hoje:
                        alunos_hoje.append(aluno)
            except Exception as e:
                print(f"Erro ao processar data para {nome}: {e}")
    
    print(f"\n🎯 Alunos com 'teste' no nome: {len(alunos_teste)}")
    if alunos_teste:
        print("\n📋 Alunos encontrados com 'teste':")
        for i, aluno in enumerate(alunos_teste):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   ID: {aluno.get('_id', 'N/A')}")
            print(f"   Telefone: {aluno.get('telefone', 'N/A')}")
            print(f"   Email: {aluno.get('email', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
            print(f"   Criado em: {aluno.get('criado_em', 'N/A')}")
            print()
    
    print(f"\n📅 Alunos cadastrados hoje ({hoje}): {len(alunos_hoje)}")
    if alunos_hoje:
        print("\n📋 Alunos cadastrados hoje:")
        for i, aluno in enumerate(alunos_hoje):
            print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
            print(f"   ID: {aluno.get('_id', 'N/A')}")
            print(f"   Telefone: {aluno.get('telefone', 'N/A')}")
            print(f"   Email: {aluno.get('email', 'N/A')}")
            print(f"   Atividade: {aluno.get('atividade', 'N/A')}")
            print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
            print(f"   Criado em: {aluno.get('criado_em', 'N/A')}")
            print()
    
    # Verificar especificamente por 'teste teste teste'
    aluno_teste_especifico = None
    for aluno in alunos:
        if aluno.get('nome', '').lower() == 'teste teste teste':
            aluno_teste_especifico = aluno
            break
    
    if aluno_teste_especifico:
        print("\n✅ ENCONTRADO: Aluno 'teste teste teste' está no banco de dados!")
        print(f"   ID: {aluno_teste_especifico.get('_id')}")
        print(f"   Data de cadastro: {aluno_teste_especifico.get('data_cadastro')}")
        print(f"   Criado em: {aluno_teste_especifico.get('criado_em')}")
    else:
        print("\n❌ NÃO ENCONTRADO: Aluno 'teste teste teste' não foi encontrado no banco.")
    
    # Verificar os 20 alunos mais recentes por data de cadastro
    print("\n📅 20 alunos mais recentes por data de cadastro:")
    alunos_com_data = [a for a in alunos if a.get('data_cadastro')]
    alunos_ordenados = sorted(alunos_com_data, key=lambda x: x.get('data_cadastro', ''), reverse=True)
    
    for i, aluno in enumerate(alunos_ordenados[:20]):
        print(f"{i+1}. Nome: {aluno.get('nome', 'N/A')}")
        print(f"   Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
        print(f"   Criado em: {aluno.get('criado_em', 'N/A')}")
        print()
    
except Exception as e:
    print(f"❌ Erro ao verificar dados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Verificação concluída!")