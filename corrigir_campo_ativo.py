#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o campo 'ativo' na tabela alunos
Todos os alunos têm ativo=None, precisa definir como True
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

def corrigir_campo_ativo():
    """Corrige o campo ativo definindo todos os alunos como ativos (True)"""
    print("\n🔧 CORRIGINDO CAMPO 'ATIVO' - DEFININDO TODOS COMO ATIVOS")
    print("=" * 65)
    
    try:
        with app.app_context():
            db_session = SessionLocal()
            
            try:
                # Verificar status atual
                print("\n📊 Status atual dos alunos:")
                total_alunos = db_session.query(Aluno).count()
                alunos_none = db_session.query(Aluno).filter(Aluno.ativo.is_(None)).count()
                alunos_true = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                alunos_false = db_session.query(Aluno).filter(Aluno.ativo == False).count()
                
                print(f"  Total de alunos: {total_alunos}")
                print(f"  Alunos com ativo = None: {alunos_none}")
                print(f"  Alunos com ativo = True: {alunos_true}")
                print(f"  Alunos com ativo = False: {alunos_false}")
                
                if alunos_none == 0:
                    print("✅ Todos os alunos já têm o campo 'ativo' definido!")
                    return
                
                # Confirmar ação
                print(f"\n⚠️  Será definido ativo=True para {alunos_none} alunos")
                print("\n🔧 Corrigindo campo 'ativo'...")
                
                # Atualizar todos os alunos com ativo=None para ativo=True
                alunos_atualizados = db_session.query(Aluno).filter(
                    Aluno.ativo.is_(None)
                ).update(
                    {Aluno.ativo: True},
                    synchronize_session=False
                )
                
                # Confirmar as mudanças
                db_session.commit()
                
                print(f"✅ {alunos_atualizados} alunos atualizados com sucesso!")
                
                # Verificar status após a atualização
                print("\n📊 Status após correção:")
                total_alunos_final = db_session.query(Aluno).count()
                alunos_none_final = db_session.query(Aluno).filter(Aluno.ativo.is_(None)).count()
                alunos_true_final = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                alunos_false_final = db_session.query(Aluno).filter(Aluno.ativo == False).count()
                
                print(f"  Total de alunos: {total_alunos_final}")
                print(f"  Alunos com ativo = None: {alunos_none_final}")
                print(f"  Alunos com ativo = True: {alunos_true_final}")
                print(f"  Alunos com ativo = False: {alunos_false_final}")
                
                # Mostrar alguns alunos corrigidos
                print("\n📋 Primeiros 5 alunos corrigidos:")
                alunos_amostra = db_session.query(Aluno).filter(
                    Aluno.ativo == True
                ).limit(5).all()
                
                for i, aluno in enumerate(alunos_amostra, 1):
                    print(f"  {i}. {aluno.nome} - ativo: {aluno.ativo} ({type(aluno.ativo).__name__})")
                
                # Testar a função obter_alunos_usuario agora
                print("\n🎯 Testando função obter_alunos_usuario após correção:")
                try:
                    from app import obter_alunos_usuario
                    
                    # Usar test_request_context para simular uma requisição
                    with app.test_request_context():
                        with app.test_client() as client:
                            # Simular sessão de usuário
                            with client.session_transaction() as sess:
                                sess['usuario_logado'] = 'admin'
                                sess['nivel_usuario'] = 'admin'
                            
                            # Chamar a função
                            alunos_resultado = obter_alunos_usuario()
                            print(f"📊 Total de alunos retornados pela função: {len(alunos_resultado)}")
                            
                            if alunos_resultado:
                                print("\n📋 Primeiros 3 alunos da função:")
                                for i, aluno in enumerate(alunos_resultado[:3], 1):
                                    atividade_nome = aluno.atividade.nome if aluno.atividade else 'Sem atividade'
                                    print(f"  {i}. {aluno.nome} - {atividade_nome}")
                            else:
                                print("⚠️  Ainda nenhum aluno retornado pela função")
                                
                except Exception as e:
                    print(f"❌ Erro ao testar função: {e}")
                
            except Exception as e:
                print(f"❌ Erro durante a correção: {e}")
                db_session.rollback()
                import traceback
                traceback.print_exc()
            
            finally:
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 65)
    print(f"🏁 CORREÇÃO CONCLUÍDA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("\n⚠️  ATENÇÃO: Este script irá definir ativo=True para TODOS os alunos com ativo=None!")
    print("Pressione ENTER para continuar ou Ctrl+C para cancelar...")
    input()
    
    corrigir_campo_ativo()