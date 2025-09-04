#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do app Flask local com SQLite
"""

import os
import sys
from dotenv import load_dotenv

# Forçar uso do .env local (não .env.production)
if os.path.exists('.env'):
    load_dotenv('.env')
    print("📋 Carregando configurações locais (.env)")
else:
    print("⚠️  Arquivo .env não encontrado")

# Importar após carregar as variáveis de ambiente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import obter_alunos_usuario
    print("✅ Função obter_alunos_usuario importada com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar função: {e}")
    sys.exit(1)

def testar_app_local():
    """Testa a função obter_alunos_usuario no ambiente local"""
    print("\n🚀 TESTE APP LOCAL - FUNÇÃO obter_alunos_usuario")
    print("=" * 60)
    
    # Verificar configuração do banco
    database_url = os.environ.get('DATABASE_URL')
    print(f"🗄️  DATABASE_URL: {database_url}")
    
    try:
        # Criar contexto Flask para simular sessão
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = 'teste_local'
        
        with app.test_request_context():
            from flask import session
            
            # Simular login como admin
            session['usuario_logado'] = 'admin'
            session['usuario_nivel'] = 'admin'
            
            print(f"👤 Testando como: admin (nível: admin)")
            
            # Chamar a função (sem parâmetros)
            alunos = obter_alunos_usuario()
            
            print(f"📊 Total de alunos retornados: {len(alunos)}")
            
            if len(alunos) > 0:
                print("\n📋 Primeiros 5 alunos:")
                for i, aluno in enumerate(alunos[:5], 1):
                    nome = aluno.get('nome', 'N/A')
                    atividade = aluno.get('atividade', 'N/A')
                    print(f"  {i}. {nome} - {atividade}")
            else:
                print("⚠️  Nenhum aluno encontrado")
            
            return len(alunos)
        
    except Exception as e:
        print(f"❌ Erro ao executar função: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    testar_app_local()