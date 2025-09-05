#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from models import init_mongodb, AlunoDAO, AtividadeDAO
import sys

print("🔧 Corrigindo campo 'atividade' dos alunos no AMBIENTE DE PRODUÇÃO...")

# Carregar variáveis de ambiente de produção
load_dotenv('.env.production')
print(f"📍 Usando banco: {os.getenv('MONGO_DATABASE')}")
print(f"📍 Cluster: {os.getenv('MONGO_CLUSTER')}")

# Inicializar MongoDB com configurações de produção
db = init_mongodb()

try:
    print("\n📊 Verificando dados dos alunos no ambiente de produção...")
    
    # Listar todos os alunos
    alunos = AlunoDAO.listar_todos()
    print(f"Total de alunos encontrados: {len(alunos)}")
    
    # Listar todas as atividades para fazer o mapeamento
    atividades = AtividadeDAO.listar_todas()
    atividades_map = {str(ativ.get('_id')): ativ.get('nome') for ativ in atividades}
    
    print(f"\n🎯 Atividades disponíveis: {len(atividades)}")
    for ativ_id, nome in atividades_map.items():
        print(f"- ID: {ativ_id} -> Nome: {nome}")
    
    alunos_corrigidos = 0
    alunos_sem_atividade = 0
    alunos_ja_com_atividade = 0
    
    print("\n🔄 Processando alunos...")
    
    for aluno in alunos:
        aluno_id = aluno.get('_id')
        nome_aluno = aluno.get('nome', 'N/A')
        atividades_ids = aluno.get('atividades_ids', [])
        atividade_atual = aluno.get('atividade', '')
        
        # Se já tem atividade preenchida, pular
        if atividade_atual and atividade_atual.strip():
            alunos_ja_com_atividade += 1
            continue
            
        # Se tem atividades_ids, converter para atividade
        if atividades_ids and len(atividades_ids) > 0:
            # Pegar a primeira atividade da lista
            primeira_atividade_id = str(atividades_ids[0])
            
            if primeira_atividade_id in atividades_map:
                nome_atividade = atividades_map[primeira_atividade_id]
                
                # Atualizar o aluno com o campo 'atividade'
                dados_atualizacao = {
                    'atividade': nome_atividade
                }
                
                AlunoDAO.atualizar(aluno_id, dados_atualizacao)
                print(f"✅ {nome_aluno} -> Atividade: {nome_atividade}")
                alunos_corrigidos += 1
            else:
                print(f"⚠️  {nome_aluno} -> ID de atividade não encontrado: {primeira_atividade_id}")
                # Definir como "Cadastro Geral" mesmo assim
                dados_atualizacao = {
                    'atividade': 'Cadastro Geral'
                }
                AlunoDAO.atualizar(aluno_id, dados_atualizacao)
                alunos_corrigidos += 1
        else:
            # Se não tem atividades_ids, definir como "Cadastro Geral"
            dados_atualizacao = {
                'atividade': 'Cadastro Geral'
            }
            
            AlunoDAO.atualizar(aluno_id, dados_atualizacao)
            print(f"📝 {nome_aluno} -> Atividade: Cadastro Geral (padrão)")
            alunos_corrigidos += 1
    
    print(f"\n📊 Resumo da correção no AMBIENTE DE PRODUÇÃO:")
    print(f"✅ Alunos corrigidos: {alunos_corrigidos}")
    print(f"👍 Alunos já com atividade: {alunos_ja_com_atividade}")
    print(f"⚠️  Alunos sem atividade válida: {alunos_sem_atividade}")
    print(f"📋 Total processado: {len(alunos)}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Correção no ambiente de produção concluída!")