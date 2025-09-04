#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ativar todos os alunos no banco de dados
Todos os alunos estão com ativo=False, causando o problema de exibição
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
    from models import SessionLocal, Aluno
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def ativar_todos_alunos():
    """Ativa todos os alunos no banco de dados"""
    print("\n🔄 ATIVANDO TODOS OS ALUNOS")
    print("=" * 50)
    
    # Mostrar configuração do banco
    database_url = os.getenv('DATABASE_URL')
    print(f"🗄️  DATABASE_URL: {database_url}")
    
    try:
        with app.app_context():
            db_session = SessionLocal()
            
            try:
                # Verificar status atual
                print("\n📊 Status atual dos alunos:")
                total_alunos = db_session.query(Aluno).count()
                alunos_ativos = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                alunos_inativos = db_session.query(Aluno).filter(Aluno.ativo == False).count()
                
                print(f"  Total de alunos: {total_alunos}")
                print(f"  Alunos ativos: {alunos_ativos}")
                print(f"  Alunos inativos: {alunos_inativos}")
                
                if alunos_inativos == 0:
                    print("✅ Todos os alunos já estão ativos!")
                    return
                
                # Confirmar ação
                print(f"\n⚠️  Será ativado {alunos_inativos} alunos")
                print("\n🔄 Ativando alunos...")
                
                # Atualizar todos os alunos inativos para ativo=True
                alunos_atualizados = db_session.query(Aluno).filter(
                    Aluno.ativo == False
                ).update(
                    {Aluno.ativo: True},
                    synchronize_session=False
                )
                
                # Confirmar as mudanças
                db_session.commit()
                
                print(f"✅ {alunos_atualizados} alunos ativados com sucesso!")
                
                # Verificar status após a atualização
                print("\n📊 Status após ativação:")
                total_alunos_final = db_session.query(Aluno).count()
                alunos_ativos_final = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                alunos_inativos_final = db_session.query(Aluno).filter(Aluno.ativo == False).count()
                
                print(f"  Total de alunos: {total_alunos_final}")
                print(f"  Alunos ativos: {alunos_ativos_final}")
                print(f"  Alunos inativos: {alunos_inativos_final}")
                
                # Mostrar alguns alunos ativados
                print("\n📋 Primeiros 5 alunos ativados:")
                alunos_amostra = db_session.query(Aluno).filter(
                    Aluno.ativo == True
                ).limit(5).all()
                
                for i, aluno in enumerate(alunos_amostra, 1):
                    print(f"  {i}. {aluno.nome} - Ativo: {aluno.ativo}")
                
            except Exception as e:
                print(f"❌ Erro durante a ativação: {e}")
                db_session.rollback()
                import traceback
                traceback.print_exc()
            
            finally:
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🏁 ATIVAÇÃO CONCLUÍDA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO: Este script irá ativar TODOS os alunos no banco de dados!")
    print("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    input()
    
    ativar_todos_alunos()