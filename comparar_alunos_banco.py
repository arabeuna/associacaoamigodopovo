#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar alunos do banco MongoDB com os que aparecem no sistema
Verifica diferenças entre dados do banco e dados carregados no sistema
"""

import os
from datetime import datetime

print("🔍 COMPARAÇÃO: ALUNOS NO BANCO vs SISTEMA")
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

# 1. Verificar conexão direta com MongoDB
print("\n🔗 1. VERIFICANDO DADOS NO MONGODB:")
try:
    from models import AlunoDAO
    
    # Buscar todos os alunos no banco
    alunos_banco = AlunoDAO.listar_todos()
    print(f"✅ Total de alunos no banco: {len(alunos_banco)}")
    
    if len(alunos_banco) > 0:
        print("\n📊 PRIMEIROS 20 ALUNOS NO BANCO:")
        for i, aluno in enumerate(alunos_banco[:20], 1):
            nome = aluno.get('nome', 'N/A')
            atividade = aluno.get('atividade', 'N/A')
            print(f"   {i:2d}. {nome} - {atividade}")
        
        # Verificar se os alunos da imagem estão no banco
        print("\n🔍 VERIFICANDO ALUNOS DA IMAGEM NO BANCO:")
        nomes_banco = [aluno.get('nome', '').upper() for aluno in alunos_banco]
        
        encontrados = []
        nao_encontrados = []
        
        for nome_imagem in alunos_imagem:
            if nome_imagem.upper() in nomes_banco:
                encontrados.append(nome_imagem)
                # Buscar dados completos
                for aluno in alunos_banco:
                    if aluno.get('nome', '').upper() == nome_imagem.upper():
                        print(f"   ✅ {nome_imagem}")
                        print(f"      Atividade: {aluno.get('atividade', 'N/A')}")
                        print(f"      Turma: {aluno.get('turma', 'N/A')}")
                        print(f"      Data Cadastro: {aluno.get('data_cadastro', 'N/A')}")
                        break
            else:
                nao_encontrados.append(nome_imagem)
                print(f"   ❌ {nome_imagem} - NÃO ENCONTRADO")
        
        print(f"\n📊 RESUMO DA VERIFICAÇÃO:")
        print(f"   Encontrados no banco: {len(encontrados)}/{len(alunos_imagem)}")
        print(f"   Não encontrados: {len(nao_encontrados)}")
        
        if nao_encontrados:
            print(f"\n❌ ALUNOS NÃO ENCONTRADOS NO BANCO:")
            for nome in nao_encontrados:
                print(f"   - {nome}")
    
except Exception as e:
    print(f"❌ Erro ao acessar banco: {e}")
    import traceback
    traceback.print_exc()

# 2. Verificar dados carregados no sistema
print("\n🏫 2. VERIFICANDO DADOS CARREGADOS NO SISTEMA:")
try:
    from app import academia
    
    if academia and hasattr(academia, 'alunos_reais'):
        alunos_sistema = academia.alunos_reais
        print(f"✅ Total de alunos no sistema: {len(alunos_sistema)}")
        
        if len(alunos_sistema) > 0:
            print("\n📊 PRIMEIROS 20 ALUNOS NO SISTEMA:")
            for i, aluno in enumerate(alunos_sistema[:20], 1):
                nome = aluno.get('nome', 'N/A')
                atividade = aluno.get('atividade', 'N/A')
                print(f"   {i:2d}. {nome} - {atividade}")
            
            # Verificar se os alunos da imagem estão no sistema
            print("\n🔍 VERIFICANDO ALUNOS DA IMAGEM NO SISTEMA:")
            nomes_sistema = [aluno.get('nome', '').upper() for aluno in alunos_sistema]
            
            encontrados_sistema = []
            nao_encontrados_sistema = []
            
            for nome_imagem in alunos_imagem:
                if nome_imagem.upper() in nomes_sistema:
                    encontrados_sistema.append(nome_imagem)
                    print(f"   ✅ {nome_imagem} - ENCONTRADO NO SISTEMA")
                else:
                    nao_encontrados_sistema.append(nome_imagem)
                    print(f"   ❌ {nome_imagem} - NÃO ENCONTRADO NO SISTEMA")
            
            print(f"\n📊 RESUMO SISTEMA:")
            print(f"   Encontrados no sistema: {len(encontrados_sistema)}/{len(alunos_imagem)}")
            print(f"   Não encontrados no sistema: {len(nao_encontrados_sistema)}")
        
    else:
        print("❌ Sistema Academia não inicializado ou sem dados")
        
except Exception as e:
    print(f"❌ Erro ao acessar sistema: {e}")
    import traceback
    traceback.print_exc()

# 3. Análise de diferenças
print("\n🔍 3. ANÁLISE DE POSSÍVEIS PROBLEMAS:")
print("\n💡 POSSÍVEIS CAUSAS DOS ALUNOS NÃO APARECEREM:")
print("   1. Filtros ativos no dashboard ou lista de alunos")
print("   2. Problemas na consulta/busca do sistema")
print("   3. Dados com campos obrigatórios em branco")
print("   4. Problemas de codificação de caracteres")
print("   5. Status 'ativo' definido como False")
print("   6. Problemas na renderização do frontend")

print("\n🔧 PRÓXIMOS PASSOS RECOMENDADOS:")
print("   1. Verificar se há filtros ativos na interface")
print("   2. Verificar campos obrigatórios dos alunos")
print("   3. Testar busca específica por nome")
print("   4. Verificar logs do sistema")
print("   5. Testar carregamento sem cache")

print("\n" + "=" * 60)
print("🎯 COMPARAÇÃO CONCLUÍDA")