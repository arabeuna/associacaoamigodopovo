#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico completo para ambiente de produção
Testa conectividade, estrutura do banco e função obter_alunos_usuario
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Carregar configurações de produção
print("📋 Carregando configurações de produção (.env.production)")
load_dotenv('.env.production', override=True)

# Importar módulos necessários
try:
    from app import app, obter_alunos_usuario
    from models import SessionLocal, Aluno, Atividade, Turma, engine
    from database_integration_robusto import db_integration_robusto
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def testar_producao():
    """Executa bateria completa de testes no ambiente de produção"""
    print("\n🚀 TESTE COMPLETO - AMBIENTE DE PRODUÇÃO")
    print("=" * 60)
    
    # Mostrar configuração do banco
    database_url = os.getenv('DATABASE_URL')
    print(f"🗄️  DATABASE_URL: {database_url}")
    
    try:
        with app.app_context():
            # Criar sessão do banco
            db_session = SessionLocal()
            
            try:
                # TESTE 1: Conectividade com banco de dados
                print("\n🔌 TESTE 1: Conectividade com banco de dados")
                try:
                    # Contar total de alunos
                    total_alunos = db_session.query(Aluno).count()
                    print(f"✅ Conexão estabelecida - Total de alunos: {total_alunos}")
                    
                    # Contar alunos ativos
                    alunos_ativos = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                    print(f"📊 Alunos ativos: {alunos_ativos}")
                    
                except Exception as e:
                    print(f"❌ Erro na conectividade: {e}")
                    return
            
                # TESTE 2: Estrutura das tabelas
                print("\n🏗️  TESTE 2: Estrutura das tabelas")
                try:
                    # Verificar tabelas existentes
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    tabelas = inspector.get_table_names()
                    print(f"📋 Tabelas encontradas: {tabelas}")
                    
                    # Verificar colunas da tabela alunos
                    if 'alunos' in tabelas:
                        colunas_alunos = inspector.get_columns('alunos')
                        print(f"🔍 Colunas da tabela alunos: {[col['name'] for col in colunas_alunos]}")
                    
                except Exception as e:
                    print(f"❌ Erro ao verificar estrutura: {e}")
            
                # TESTE 3: Amostra de dados
                print("\n📊 TESTE 3: Amostra de dados")
                try:
                    # Buscar primeiros 5 alunos com atividade
                    alunos_amostra = db_session.query(Aluno, Atividade).join(
                        Atividade, Aluno.atividade_id == Atividade.id
                    ).limit(5).all()
                    
                    print("📋 Primeiros 5 alunos:")
                    for i, (aluno, atividade) in enumerate(alunos_amostra, 1):
                        print(f"  {i}. {aluno.nome} - {atividade.nome}")
                        
                except Exception as e:
                    print(f"❌ Erro ao buscar amostra: {e}")
            
                # TESTE 4: Função obter_alunos_usuario
                print("\n🎯 TESTE 4: Função obter_alunos_usuario")
                try:
                    # Simular sessão de administrador
                    from flask import session
                    session['usuario_logado'] = 'admin'
                    session['nivel_usuario'] = 'admin'
                    
                    print(f"👤 Testando como: {session.get('usuario_logado')} (nível: {session.get('nivel_usuario')})")
                    
                    # Chamar a função
                    alunos_resultado = obter_alunos_usuario()
                    print(f"📊 Total de alunos retornados pela função: {len(alunos_resultado)}")
                    
                    if alunos_resultado:
                        print("\n📋 Primeiros 5 alunos da função:")
                        for i, aluno in enumerate(alunos_resultado[:5], 1):
                            atividade_nome = aluno.atividade.nome if aluno.atividade else 'Sem atividade'
                            print(f"  {i}. {aluno.nome} - {atividade_nome}")
                    else:
                        print("⚠️  Nenhum aluno retornado pela função")
                        
                except Exception as e:
                    print(f"❌ Erro na função obter_alunos_usuario: {e}")
                    import traceback
                    traceback.print_exc()
            
                # TESTE 5: Performance e timeout
                print("\n⏱️  TESTE 5: Performance")
                try:
                    import time
                    start_time = time.time()
                    
                    # Consulta mais complexa para testar performance
                    resultado_complexo = db_session.query(Aluno).join(
                        Atividade, Aluno.atividade_id == Atividade.id
                    ).filter(Aluno.ativo == True).all()
                    
                    end_time = time.time()
                    tempo_execucao = end_time - start_time
                    
                    print(f"⚡ Consulta complexa executada em {tempo_execucao:.2f}s")
                    print(f"📊 Resultados: {len(resultado_complexo)} alunos")
                    
                    if tempo_execucao > 5:
                        print("⚠️  ALERTA: Consulta demorou mais de 5 segundos")
                        
                except Exception as e:
                    print(f"❌ Erro no teste de performance: {e}")
                    
            finally:
                # Fechar sessão do banco
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🏁 TESTE CONCLUÍDO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    testar_producao()