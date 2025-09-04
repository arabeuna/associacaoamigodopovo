#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples - Verificar quantos alunos são retornados pela função obter_alunos_usuario()
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("📋 Carregando configurações de produção (.env.production)")
else:
    load_dotenv()
    print("📋 Carregando configurações de desenvolvimento (.env)")

def testar_conexao_banco():
    """Testa conexão direta com o banco de dados"""
    print("\n🔍 TESTANDO CONEXÃO DIRETA COM BANCO")
    print("=" * 50)
    
    try:
        from models import SessionLocal, Aluno, Atividade
        
        db = SessionLocal()
        
        # Contar total de alunos ativos
        total_alunos = db.query(Aluno).filter(Aluno.ativo == True).count()
        print(f"✅ Conexão bem-sucedida")
        print(f"📊 Total de alunos ativos: {total_alunos}")
        
        # Verificar se há mais de 400 alunos
        if total_alunos > 400:
            print(f"✅ Banco tem mais de 400 alunos ({total_alunos})")
        else:
            print(f"⚠️  Banco tem apenas {total_alunos} alunos")
        
        # Buscar alguns alunos para teste
        primeiros_10 = db.query(Aluno).filter(Aluno.ativo == True).limit(10).all()
        print(f"\n📋 Primeiros 10 alunos:")
        for i, aluno in enumerate(primeiros_10, 1):
            print(f"   {i}. {aluno.nome} (ID: {aluno.id})")
        
        # Buscar últimos 10 alunos
        ultimos_10 = db.query(Aluno).filter(Aluno.ativo == True).order_by(Aluno.id.desc()).limit(10).all()
        print(f"\n📋 Últimos 10 alunos:")
        for i, aluno in enumerate(ultimos_10, 1):
            print(f"   {i}. {aluno.nome} (ID: {aluno.id})")
        
        db.close()
        return total_alunos
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return 0

def testar_funcao_obter_alunos():
    """Testa a função obter_alunos_usuario() diretamente"""
    print("\n🔍 TESTANDO FUNÇÃO obter_alunos_usuario()")
    print("=" * 50)
    
    try:
        # Simular sessão de admin
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = 'teste'
        
        with app.test_request_context():
            from flask import session
            
            # Simular login como admin
            session['usuario_logado'] = 'admin'
            session['usuario_nivel'] = 'admin'
            
            # Importar e testar a função
            sys.path.append('.')
            from app import obter_alunos_usuario
            
            alunos = obter_alunos_usuario()
            
            print(f"✅ Função executada com sucesso")
            print(f"📊 Total de alunos retornados: {len(alunos)}")
            
            if len(alunos) > 400:
                print(f"✅ Função retorna mais de 400 alunos ({len(alunos)})")
            else:
                print(f"⚠️  Função retorna apenas {len(alunos)} alunos")
            
            if alunos:
                print(f"\n👤 Primeiro aluno: {alunos[0].get('nome', 'N/A')}")
                print(f"👤 Último aluno: {alunos[-1].get('nome', 'N/A')}")
            
            return len(alunos)
            
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Função principal"""
    print("🚀 TESTE SIMPLES - VERIFICAÇÃO DE ALUNOS")
    print("=" * 60)
    
    # Teste 1: Conexão direta com banco
    total_banco = testar_conexao_banco()
    
    # Teste 2: Função obter_alunos_usuario()
    total_funcao = testar_funcao_obter_alunos()
    
    # Comparação
    print(f"\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"🗄️  Total no banco: {total_banco}")
    print(f"⚙️  Total da função: {total_funcao}")
    
    if total_banco != total_funcao:
        diferenca = total_banco - total_funcao
        print(f"⚠️  DIFERENÇA ENCONTRADA: {diferenca} alunos")
        if diferenca > 0:
            print(f"   A função está retornando {diferenca} alunos a menos")
        else:
            print(f"   A função está retornando {abs(diferenca)} alunos a mais")
    else:
        print(f"✅ Banco e função retornam o mesmo número de alunos")
    
    # Diagnóstico
    print(f"\n🔍 DIAGNÓSTICO")
    print("=" * 50)
    
    if total_banco > 400 and total_funcao <= 400:
        print(f"❌ PROBLEMA IDENTIFICADO:")
        print(f"   - Banco tem {total_banco} alunos")
        print(f"   - Função retorna apenas {total_funcao} alunos")
        print(f"   - Possível problema na função obter_alunos_usuario()")
        print(f"\n🔧 POSSÍVEIS CAUSAS:")
        print(f"   1. Timeout na consulta SQL")
        print(f"   2. Limitação de memória")
        print(f"   3. Erro na lógica da função")
        print(f"   4. Problema na sessão do usuário")
    elif total_banco <= 400:
        print(f"ℹ️  Banco tem apenas {total_banco} alunos")
        print(f"   - Não há problema de limitação")
        print(f"   - Verificar se dados foram migrados corretamente")
    else:
        print(f"✅ Tudo funcionando corretamente")
        print(f"   - Banco e função retornam mais de 400 alunos")

if __name__ == "__main__":
    main()