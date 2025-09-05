#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para verificar se o template está renderizando corretamente
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente de produção
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Carregando variáveis de ambiente de produção (.env.production)")
else:
    print("❌ Arquivo .env.production não encontrado")
    sys.exit(1)

print("\n🧪 TESTE DE DADOS PARA TEMPLATE:")
print("="*50)

try:
    # Importar e inicializar o app
    from app import app, obter_alunos_usuario
    
    with app.app_context():
        with app.test_request_context():
            from flask import session
            
            # Simular login de admin
            session['usuario_logado'] = 'admin'
            session['usuario_nome'] = 'Administrador Geral'
            session['usuario_nivel'] = 'admin'
            
            print("🔍 Obtendo dados dos alunos...")
            alunos = obter_alunos_usuario()
            print(f"✅ Obtidos {len(alunos)} alunos")
            
            if len(alunos) == 0:
                print("❌ PROBLEMA: Nenhum aluno foi retornado pela função!")
                
                # Tentar acesso direto ao banco
                print("\n🔍 Tentando acesso direto ao banco...")
                from database_integration import DatabaseIntegration
                db_integration = DatabaseIntegration()
                
                # Buscar diretamente na coleção
                alunos_direto = list(db_integration.alunos_collection.find({}))
                print(f"📊 Alunos encontrados diretamente no banco: {len(alunos_direto)}")
                
                if len(alunos_direto) > 0:
                    print("❌ PROBLEMA IDENTIFICADO: Os dados existem no banco, mas obter_alunos_usuario() não os retorna!")
                    print("🔍 Primeiro aluno do banco:")
                    primeiro = alunos_direto[0]
                    print(f"   - ID: {primeiro.get('_id')}")
                    print(f"   - Nome: {primeiro.get('nome')}")
                    print(f"   - Atividade: {primeiro.get('atividade')}")
                    print(f"   - Status: {primeiro.get('status')}")
                else:
                    print("❌ PROBLEMA: Não há dados no banco de dados!")
                
                sys.exit(1)
            
            print("\n📊 ANÁLISE DOS DADOS OBTIDOS:")
            print(f"   - Total de alunos: {len(alunos)}")
            
            if len(alunos) > 0:
                primeiro_aluno = alunos[0]
                print(f"   - Primeiro aluno: {primeiro_aluno.get('nome', 'N/A')}")
                print(f"   - Atividade: {primeiro_aluno.get('atividade', 'N/A')}")
                print(f"   - Status: {primeiro_aluno.get('status', 'N/A')}")
                print(f"   - Turma: {primeiro_aluno.get('turma', 'N/A')}")
                
                # Verificar estrutura dos dados
                print("\n🔍 ESTRUTURA DOS DADOS:")
                print(f"   - Tipo do primeiro aluno: {type(primeiro_aluno)}")
                print(f"   - Chaves disponíveis: {list(primeiro_aluno.keys()) if isinstance(primeiro_aluno, dict) else 'N/A'}")
                
                # Verificar se os dados estão no formato esperado pelo template
                campos_esperados = ['nome', 'telefone', 'atividade', 'turma', 'status', 'data_cadastro']
                campos_faltando = []
                
                for campo in campos_esperados:
                    if campo not in primeiro_aluno:
                        campos_faltando.append(campo)
                
                if campos_faltando:
                    print(f"⚠️  ATENÇÃO: Campos faltando: {campos_faltando}")
                else:
                    print("✅ Todos os campos esperados estão presentes")
                
                # Simular o que o template faria
                print("\n🎨 SIMULAÇÃO DO TEMPLATE:")
                print(f"   - Condição 'if alunos': {bool(alunos)}")
                print(f"   - Tamanho da lista: {len(alunos)}")
                print(f"   - Loop funcionaria: {len(alunos) > 0}")
                
                # Verificar se há problemas com os dados
                problemas = []
                for i, aluno in enumerate(alunos[:5]):  # Verificar apenas os primeiros 5
                    if not aluno.get('nome'):
                        problemas.append(f"Aluno {i+1} sem nome")
                    if not isinstance(aluno, dict):
                        problemas.append(f"Aluno {i+1} não é um dicionário")
                
                if problemas:
                    print(f"⚠️  PROBLEMAS ENCONTRADOS: {problemas}")
                else:
                    print("✅ Dados parecem estar corretos para o template")
            
            print("\n🎯 CONCLUSÃO:")
            if len(alunos) > 0:
                print("✅ Os dados estão sendo obtidos corretamente")
                print("✅ O problema provavelmente NÃO está na obtenção dos dados")
                print("🔍 O problema pode estar na renderização do template ou na rota")
            else:
                print("❌ O problema está na obtenção dos dados")
                print("🔍 A função obter_alunos_usuario() não está retornando dados")
    
except Exception as e:
    print(f"❌ ERRO DURANTE O TESTE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)