#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar inserção do aluno "teste teste teste" no sistema
Verifica se o sistema está funcionando corretamente após as correções
"""

import os
from dotenv import load_dotenv
from models import init_mongodb, AlunoDAO, AtividadeDAO
from datetime import datetime
import sys

print("🧪 TESTE DE INSERÇÃO DE ALUNO - SISTEMA CORRIGIDO")
print("=" * 60)

# Carregar variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Carregando .env.production")
else:
    load_dotenv()
    print("✅ Carregando .env padrão")

# Inicializar MongoDB
print("\n🔄 Inicializando MongoDB...")
db = init_mongodb()

if db is None:
    print("❌ Falha ao conectar ao MongoDB")
    sys.exit(1)

print("✅ MongoDB conectado com sucesso")

try:
    # 1. Verificar estado atual
    print("\n📊 ESTADO ATUAL DO SISTEMA:")
    print("-" * 40)
    
    alunos_total = len(AlunoDAO.listar_todos())
    print(f"Total de alunos: {alunos_total}")
    
    atividades = AtividadeDAO.listar_todas()
    print(f"Total de atividades: {len(atividades)}")
    
    # Listar atividades disponíveis
    print("\nAtividades disponíveis:")
    for ativ in atividades[:5]:  # Mostrar apenas as primeiras 5
        print(f"- {ativ.get('nome', 'N/A')}")
    
    # 2. Verificar se o aluno "teste teste teste" já existe
    print("\n🔍 VERIFICANDO ALUNO 'teste teste teste':")
    print("-" * 40)
    
    alunos_teste = AlunoDAO.buscar_por_nome("teste teste teste")
    
    if alunos_teste:
        print(f"✅ Aluno 'teste teste teste' JÁ EXISTE:")
        for aluno in alunos_teste:
            print(f"   - Nome: {aluno.get('nome')}")
            print(f"   - Telefone: {aluno.get('telefone', 'N/A')}")
            print(f"   - Atividade: {aluno.get('atividade', 'N/A')}")
            print(f"   - Data cadastro: {aluno.get('data_cadastro', 'N/A')}")
    else:
        print("❌ Aluno 'teste teste teste' NÃO ENCONTRADO")
        
        # 3. Tentar inserir o aluno
        print("\n➕ INSERINDO ALUNO 'teste teste teste':")
        print("-" * 40)
        
        # Dados do novo aluno
        dados_aluno = {
            'nome': 'teste teste teste',
            'telefone': '(11) 99999-9999',
            'atividade': 'Cadastro Geral',
            'data_nascimento': '01/01/1990',
            'endereco': 'Rua de Teste, 123',
            'observacoes': 'Aluno de teste inserido manualmente',
            'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ativo': True
        }
        
        try:
            # Inserir aluno
            resultado = AlunoDAO.criar(dados_aluno)
            
            if resultado:
                print("✅ Aluno inserido com SUCESSO!")
                print(f"   - ID: {resultado}")
                
                # Verificar se foi realmente inserido
                aluno_inserido = AlunoDAO.buscar_por_nome("teste teste teste")
                if aluno_inserido:
                    print("✅ Verificação: Aluno encontrado no banco após inserção")
                    for aluno in aluno_inserido:
                        print(f"   - Nome: {aluno.get('nome')}")
                        print(f"   - Telefone: {aluno.get('telefone')}")
                        print(f"   - Atividade: {aluno.get('atividade')}")
                else:
                    print("❌ Erro: Aluno não encontrado após inserção")
            else:
                print("❌ Falha ao inserir aluno")
                
        except Exception as e:
            print(f"❌ Erro ao inserir aluno: {e}")
    
    # 4. Verificar total final
    print("\n📊 ESTADO FINAL DO SISTEMA:")
    print("-" * 40)
    
    alunos_final = len(AlunoDAO.listar_todos())
    print(f"Total de alunos: {alunos_final}")
    
    if alunos_final > alunos_total:
        print(f"✅ Novo aluno adicionado! (+{alunos_final - alunos_total})")
    else:
        print("ℹ️ Nenhum aluno novo adicionado (já existia)")
    
    # 5. Mostrar últimos alunos cadastrados
    print("\n📋 ÚLTIMOS 5 ALUNOS CADASTRADOS:")
    print("-" * 40)
    
    try:
        # Buscar alunos ordenados por data de cadastro
        from pymongo import DESCENDING
        from models import get_db
        db_conn = get_db()
        ultimos_alunos = list(db_conn.alunos.find({}, {
            'nome': 1, 
            'telefone': 1, 
            'atividade': 1, 
            'data_cadastro': 1
        }).sort('data_cadastro', DESCENDING).limit(5))
        
        for i, aluno in enumerate(ultimos_alunos, 1):
            nome = aluno.get('nome', 'N/A')
            telefone = aluno.get('telefone', 'N/A')
            atividade = aluno.get('atividade', 'N/A')
            data_cadastro = aluno.get('data_cadastro', 'N/A')
            print(f"{i}. {nome} - {telefone} - {atividade} - {data_cadastro}")
            
    except Exception as e:
        print(f"⚠️ Erro ao buscar últimos alunos: {e}")
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    
except Exception as e:
    print(f"❌ ERRO durante o teste: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("TESTE FINALIZADO")