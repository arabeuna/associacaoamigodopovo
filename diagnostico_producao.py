#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Problema de Exibição de Cadastros em Produção

Este script testa a conectividade e consultas do banco de dados
para identificar por que a produção não está mostrando mais de 400 cadastros
enquanto o localhost funciona corretamente.
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("📋 Carregando configurações de produção (.env.production)")
else:
    load_dotenv()
    print("📋 Carregando configurações de desenvolvimento (.env)")

# Configurações
LOCALHOST_URL = "http://localhost:5000"
PRODUCTION_URL = "https://associacaoamigodopovo.onrender.com"  # Substitua pela URL real

# Credenciais de teste
CREDENCIAIS_TESTE = {
    'username': 'admin',
    'password': 'admin123'
}

def testar_conexao_banco_local():
    """Testa conexão com banco de dados local"""
    print("\n🔍 TESTANDO CONEXÃO COM BANCO LOCAL")
    print("=" * 50)
    
    try:
        from models import SessionLocal, Aluno
        
        db = SessionLocal()
        
        # Contar total de alunos
        total_alunos = db.query(Aluno).filter(Aluno.ativo == True).count()
        print(f"✅ Conexão local bem-sucedida")
        print(f"📊 Total de alunos ativos no banco local: {total_alunos}")
        
        # Buscar primeiros 10 alunos
        primeiros_alunos = db.query(Aluno).filter(Aluno.ativo == True).limit(10).all()
        print(f"📋 Primeiros 10 alunos encontrados:")
        for i, aluno in enumerate(primeiros_alunos, 1):
            print(f"   {i}. {aluno.nome} (ID: {aluno.id})")
        
        db.close()
        return True, total_alunos
        
    except Exception as e:
        print(f"❌ Erro na conexão local: {e}")
        return False, 0

def fazer_login(base_url, credenciais):
    """Faz login e retorna a sessão"""
    session = requests.Session()
    
    try:
        # Fazer login
        login_data = {
            'username': credenciais['username'],
            'password': credenciais['password']
        }
        
        response = session.post(f"{base_url}/login", data=login_data, timeout=30)
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print(f"✅ Login realizado com sucesso em {base_url}")
            return session
        else:
            print(f"❌ Falha no login em {base_url} - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao fazer login em {base_url}: {e}")
        return None

def testar_busca_alunos(base_url, session, ambiente):
    """Testa a busca de alunos via API"""
    print(f"\n🔍 TESTANDO BUSCA DE ALUNOS - {ambiente.upper()}")
    print("=" * 50)
    
    try:
        # Teste 1: Busca sem termo (todos os alunos)
        print("📋 Teste 1: Busca sem termo (todos os alunos)")
        response = session.get(f"{base_url}/buscar_alunos", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                total_encontrado = data.get('total_encontrado', 0)
                alunos = data.get('alunos', [])
                print(f"✅ Busca bem-sucedida")
                print(f"📊 Total de alunos retornados: {total_encontrado}")
                print(f"📋 Tamanho da lista de alunos: {len(alunos)}")
                
                if alunos:
                    print(f"👤 Primeiro aluno: {alunos[0].get('nome', 'N/A')}")
                    print(f"👤 Último aluno: {alunos[-1].get('nome', 'N/A')}")
                
                return total_encontrado, len(alunos)
            else:
                print(f"❌ Busca falhou: {data.get('message', 'Erro desconhecido')}")
                return 0, 0
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            return 0, 0
            
    except Exception as e:
        print(f"❌ Erro na busca de alunos: {e}")
        return 0, 0

def testar_busca_com_termo(base_url, session, ambiente, termo="João"):
    """Testa busca com termo específico"""
    print(f"\n🔍 TESTANDO BUSCA COM TERMO '{termo}' - {ambiente.upper()}")
    print("=" * 50)
    
    try:
        response = session.get(f"{base_url}/buscar_alunos?termo={termo}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                total_encontrado = data.get('total_encontrado', 0)
                alunos = data.get('alunos', [])
                print(f"✅ Busca com termo bem-sucedida")
                print(f"📊 Total encontrado para '{termo}': {total_encontrado}")
                
                if alunos:
                    print(f"📋 Primeiros resultados:")
                    for i, aluno in enumerate(alunos[:5], 1):
                        print(f"   {i}. {aluno.get('nome', 'N/A')}")
                
                return total_encontrado
            else:
                print(f"❌ Busca com termo falhou: {data.get('message', 'Erro desconhecido')}")
                return 0
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Erro na busca com termo: {e}")
        return 0

def testar_ambiente(base_url, ambiente):
    """Testa um ambiente específico (localhost ou produção)"""
    print(f"\n🌐 INICIANDO TESTES - {ambiente.upper()}")
    print("=" * 60)
    
    # Fazer login
    session = fazer_login(base_url, CREDENCIAIS_TESTE)
    if not session:
        return None
    
    # Testar busca de alunos
    total_api, len_lista = testar_busca_alunos(base_url, session, ambiente)
    
    # Testar busca com termo
    total_termo = testar_busca_com_termo(base_url, session, ambiente)
    
    return {
        'ambiente': ambiente,
        'url': base_url,
        'total_alunos_api': total_api,
        'tamanho_lista': len_lista,
        'busca_termo': total_termo,
        'login_sucesso': True
    }

def comparar_resultados(resultado_local, resultado_producao):
    """Compara os resultados entre localhost e produção"""
    print("\n📊 COMPARAÇÃO DE RESULTADOS")
    print("=" * 60)
    
    if not resultado_local or not resultado_producao:
        print("❌ Não foi possível comparar - um dos ambientes falhou")
        return
    
    print(f"🏠 LOCALHOST:")
    print(f"   Total de alunos: {resultado_local['total_alunos_api']}")
    print(f"   Tamanho da lista: {resultado_local['tamanho_lista']}")
    print(f"   Busca por termo: {resultado_local['busca_termo']}")
    
    print(f"\n☁️  PRODUÇÃO:")
    print(f"   Total de alunos: {resultado_producao['total_alunos_api']}")
    print(f"   Tamanho da lista: {resultado_producao['tamanho_lista']}")
    print(f"   Busca por termo: {resultado_producao['busca_termo']}")
    
    # Análise das diferenças
    print(f"\n🔍 ANÁLISE:")
    
    diff_total = resultado_local['total_alunos_api'] - resultado_producao['total_alunos_api']
    if diff_total != 0:
        print(f"⚠️  DIFERENÇA NO TOTAL: {diff_total} alunos")
        if diff_total > 0:
            print(f"   Localhost tem {diff_total} alunos a mais que produção")
        else:
            print(f"   Produção tem {abs(diff_total)} alunos a mais que localhost")
    else:
        print(f"✅ Total de alunos é igual nos dois ambientes")
    
    diff_lista = resultado_local['tamanho_lista'] - resultado_producao['tamanho_lista']
    if diff_lista != 0:
        print(f"⚠️  DIFERENÇA NO TAMANHO DA LISTA: {diff_lista}")
        if diff_lista > 0:
            print(f"   Localhost retorna {diff_lista} alunos a mais na lista")
        else:
            print(f"   Produção retorna {abs(diff_lista)} alunos a mais na lista")
    else:
        print(f"✅ Tamanho da lista é igual nos dois ambientes")

def main():
    """Função principal do diagnóstico"""
    print("🚀 DIAGNÓSTICO DE PRODUÇÃO - SISTEMA ACADEMIA")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🎯 Objetivo: Identificar por que produção não mostra mais de 400 cadastros")
    
    # Teste 1: Conexão com banco local
    sucesso_local, total_banco_local = testar_conexao_banco_local()
    
    # Teste 2: Ambiente localhost
    print(f"\n" + "="*60)
    resultado_localhost = testar_ambiente(LOCALHOST_URL, "localhost")
    
    # Teste 3: Ambiente produção
    print(f"\n" + "="*60)
    resultado_producao = testar_ambiente(PRODUCTION_URL, "produção")
    
    # Comparação final
    if resultado_localhost and resultado_producao:
        comparar_resultados(resultado_localhost, resultado_producao)
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES")
    print("=" * 60)
    
    if sucesso_local and total_banco_local > 400:
        print(f"✅ Banco local tem {total_banco_local} alunos - dados estão corretos")
    
    if resultado_producao and resultado_producao['total_alunos_api'] <= 400:
        print(f"⚠️  Produção limitada a {resultado_producao['total_alunos_api']} alunos")
        print(f"🔧 Possíveis causas:")
        print(f"   1. Timeout de consulta no banco de produção")
        print(f"   2. Limitação de memória no servidor")
        print(f"   3. Configuração de paginação não implementada")
        print(f"   4. Dados não migrados completamente")
        print(f"   5. Problema na função obter_alunos_usuario()")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    print(f"   1. Verificar logs do servidor de produção")
    print(f"   2. Testar consulta SQL diretamente no banco de produção")
    print(f"   3. Implementar paginação na busca de alunos")
    print(f"   4. Adicionar logs de debug na função obter_alunos_usuario()")
    print(f"   5. Verificar configurações de timeout do banco")

if __name__ == "__main__":
    main()