#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar o campo 'ativo' na tabela alunos
Investigar por que há 878 alunos mas 0 ativos e 0 inativos
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
    from app import app
    from models import SessionLocal, Aluno, engine
    from sqlalchemy import inspect, text
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def verificar_campo_ativo():
    """Verifica o campo ativo na tabela alunos"""
    print("\n🔍 VERIFICANDO CAMPO 'ATIVO' NA TABELA ALUNOS")
    print("=" * 60)
    
    try:
        with app.app_context():
            db_session = SessionLocal()
            
            try:
                # Verificar estrutura da tabela
                print("\n🏗️  Estrutura da tabela alunos:")
                inspector = inspect(engine)
                colunas = inspector.get_columns('alunos')
                
                for coluna in colunas:
                    if 'ativo' in coluna['name'].lower():
                        print(f"  📋 Coluna: {coluna['name']} - Tipo: {coluna['type']} - Nullable: {coluna['nullable']} - Default: {coluna.get('default')}")
                
                # Verificar valores únicos do campo ativo
                print("\n📊 Valores únicos do campo 'ativo':")
                try:
                    # Consulta SQL direta para ver os valores
                    result = db_session.execute(text("SELECT DISTINCT ativo, COUNT(*) as count FROM alunos GROUP BY ativo"))
                    valores_ativo = result.fetchall()
                    
                    for valor, count in valores_ativo:
                        print(f"  ativo = {valor} ({type(valor).__name__}): {count} alunos")
                        
                except Exception as e:
                    print(f"❌ Erro na consulta SQL direta: {e}")
                
                # Verificar usando SQLAlchemy ORM
                print("\n🔍 Verificação usando ORM:")
                try:
                    total_alunos = db_session.query(Aluno).count()
                    print(f"  Total de alunos: {total_alunos}")
                    
                    # Verificar valores None
                    alunos_ativo_none = db_session.query(Aluno).filter(Aluno.ativo.is_(None)).count()
                    print(f"  Alunos com ativo = None: {alunos_ativo_none}")
                    
                    # Verificar valores True
                    alunos_ativo_true = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                    print(f"  Alunos com ativo = True: {alunos_ativo_true}")
                    
                    # Verificar valores False
                    alunos_ativo_false = db_session.query(Aluno).filter(Aluno.ativo == False).count()
                    print(f"  Alunos com ativo = False: {alunos_ativo_false}")
                    
                    # Verificar valores 1
                    alunos_ativo_1 = db_session.query(Aluno).filter(Aluno.ativo == 1).count()
                    print(f"  Alunos com ativo = 1: {alunos_ativo_1}")
                    
                    # Verificar valores 0
                    alunos_ativo_0 = db_session.query(Aluno).filter(Aluno.ativo == 0).count()
                    print(f"  Alunos com ativo = 0: {alunos_ativo_0}")
                    
                except Exception as e:
                    print(f"❌ Erro na verificação ORM: {e}")
                
                # Mostrar alguns exemplos de alunos
                print("\n📋 Primeiros 10 alunos com valores do campo 'ativo':")
                try:
                    alunos_amostra = db_session.query(Aluno).limit(10).all()
                    
                    for i, aluno in enumerate(alunos_amostra, 1):
                        print(f"  {i:2d}. {aluno.nome} - ativo: {aluno.ativo} ({type(aluno.ativo).__name__})")
                        
                except Exception as e:
                    print(f"❌ Erro ao buscar amostra: {e}")
                
            except Exception as e:
                print(f"❌ Erro durante a verificação: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🏁 VERIFICAÇÃO CONCLUÍDA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    verificar_campo_ativo()