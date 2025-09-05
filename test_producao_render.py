#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para simular o ambiente de produção do Render
"""

import os
import sys
from dotenv import load_dotenv

# Simular ambiente de produção
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Carregar variáveis de ambiente de produção
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Carregando variáveis de ambiente de produção (.env.production)")
else:
    print("❌ Arquivo .env.production não encontrado")
    sys.exit(1)

print("\n🔧 SIMULANDO AMBIENTE RENDER:")
print("="*50)
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")
print(f"FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
print(f"MONGO_DATABASE: {os.environ.get('MONGO_DATABASE')}")
print(f"SECRET_KEY: {os.environ.get('SECRET_KEY', 'não definida')[:10]}...")

try:
    # Importar e inicializar o sistema
    print("\n🚀 INICIALIZANDO SISTEMA...")
    from database_integration_robusto import get_db_integration
    
    # Obter instância do banco
    db_integration = get_db_integration()
    print("✅ Database integration inicializada")
    
    # Testar função obter_alunos_usuario
    print("\n🔍 TESTANDO FUNÇÃO obter_alunos_usuario():")
    print("-" * 40)
    
    # Simular sessão de admin
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'test_key')
    
    with app.test_request_context():
        from flask import session
        
        # Simular login de admin
        session['usuario_logado'] = 'admin'
        session['usuario_nome'] = 'Administrador Geral'
        session['usuario_nivel'] = 'admin'
        
        # Importar função
        sys.path.append('.')
        from app import obter_alunos_usuario
        
        # Testar função
        print("🔍 Executando obter_alunos_usuario()...")
        alunos = obter_alunos_usuario()
        
        print(f"✅ Total de alunos retornados: {len(alunos)}")
        
        if len(alunos) > 0:
            print("\n📋 Primeiros 3 alunos:")
            for i, aluno in enumerate(alunos[:3], 1):
                nome = aluno.get('nome', 'Nome não disponível')
                atividade = aluno.get('atividade', 'Atividade não disponível')
                print(f"  {i}. {nome} - {atividade}")
        else:
            print("❌ Nenhum aluno foi retornado!")
            
            # Verificar diretamente no banco
            print("\n🔍 VERIFICAÇÃO DIRETA NO BANCO:")
            try:
                total_banco = db_integration.contar_alunos_db()
                print(f"📊 Total de alunos no banco: {total_banco}")
                
                if total_banco > 0:
                    alunos_banco = db_integration.listar_alunos_db()
                    print(f"✅ Conseguiu listar {len(alunos_banco)} alunos do banco")
                    
                    if len(alunos_banco) > 0:
                        print("\n📋 Primeiros 3 alunos do banco:")
                        for i, aluno in enumerate(alunos_banco[:3], 1):
                            nome = aluno.get('nome', 'Nome não disponível')
                            atividade = aluno.get('atividade', 'Atividade não disponível')
                            print(f"  {i}. {nome} - {atividade}")
                else:
                    print("❌ Banco não tem alunos cadastrados")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar banco diretamente: {e}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ ERRO DURANTE O TESTE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)