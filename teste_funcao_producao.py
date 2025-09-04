#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da função obter_alunos_usuario em ambiente de produção
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
    from models import SessionLocal, Aluno
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def testar_funcao_obter_alunos():
    """Testa a função obter_alunos_usuario com contexto Flask"""
    print("\n🎯 TESTE DA FUNÇÃO obter_alunos_usuario - PRODUÇÃO")
    print("=" * 60)
    
    # Mostrar configuração do banco
    database_url = os.environ.get('DATABASE_URL', 'Não configurado')
    print(f"🗄️  DATABASE_URL: {database_url[:50]}..." if len(database_url) > 50 else f"🗄️  DATABASE_URL: {database_url}")
    
    try:
        # Usar test_request_context para simular uma requisição
        with app.test_request_context():
            from flask import session
            
            # Simular login como admin
            session['usuario_logado'] = 'admin'
            session['usuario_nivel'] = 'admin'
            session['usuario_nome'] = 'Admin Teste'
            
            print(f"👤 Usuário simulado: admin (nível: admin)")
            print(f"🔍 Sessão: usuario_logado={session.get('usuario_logado')}, nivel={session.get('usuario_nivel')}")
            
            # Testar a função
            print("\n🔍 Chamando função obter_alunos_usuario()...")
            alunos_resultado = obter_alunos_usuario()
            
            print(f"📊 Total de alunos retornados: {len(alunos_resultado)}")
            
            if alunos_resultado:
                print("\n📋 Primeiros 5 alunos:")
                for i, aluno in enumerate(alunos_resultado[:5], 1):
                    nome = aluno.get('nome', 'N/A')
                    atividade = aluno.get('atividade', 'Sem atividade')
                    print(f"  {i}. {nome} - {atividade}")
                    
                print(f"\n✅ Função funcionando corretamente! {len(alunos_resultado)} alunos encontrados.")
            else:
                print("⚠️  Nenhum aluno retornado pela função")
                
                # Verificar diretamente no banco
                print("\n🔍 Verificando alunos diretamente no banco...")
                db_session = SessionLocal()
                try:
                    total_direto = db_session.query(Aluno).count()
                    ativos_direto = db_session.query(Aluno).filter(Aluno.ativo == True).count()
                    print(f"📊 Total no banco: {total_direto} (ativos: {ativos_direto})")
                    
                    if total_direto > 0:
                        print("\n📋 Primeiros 5 alunos do banco:")
                        alunos_direto = db_session.query(Aluno).limit(5).all()
                        for i, aluno in enumerate(alunos_direto, 1):
                            status = 'Ativo' if aluno.ativo else 'Inativo'
                            print(f"  {i}. {aluno.nome} ({status})")
                finally:
                    db_session.close()
            
            return len(alunos_resultado)
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Função principal"""
    total_alunos = testar_funcao_obter_alunos()
    
    print("\n" + "=" * 60)
    print(f"🏁 TESTE CONCLUÍDO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_alunos > 0:
        print(f"✅ Sucesso: {total_alunos} alunos encontrados")
    else:
        print("⚠️  Problema: Nenhum aluno encontrado")

if __name__ == "__main__":
    main()