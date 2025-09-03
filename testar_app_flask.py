#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, engine, Base
from sqlalchemy import text

def testar_models():
    try:
        print("=== Teste dos Models da Aplicação ===")
        
        # Testar engine dos models
        print(f"Engine URL: {engine.url}")
        
        # Testar conexão através do engine dos models
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()
            print(f"✅ Engine dos models conectou! Banco: {db_name[0]}")
        
        # Testar SessionLocal dos models
        session = SessionLocal()
        result = session.execute(text("SELECT COUNT(*) FROM alunos;"))
        count = result.fetchone()
        print(f"✅ SessionLocal funcionando! Alunos no banco: {count[0]}")
        session.close()
        
        # Testar criação de tabelas
        print("\n=== Testando criação de tabelas ===")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos models: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def testar_cadastro_simulado():
    try:
        print("\n=== Teste de Cadastro Simulado ===")
        
        from models import Aluno
        from datetime import date
        
        session = SessionLocal()
        
        # Criar um aluno de teste
        aluno_teste = Aluno(
            id_unico="TESTE_CONEXAO_001",
            nome="Teste Conexão",
            data_nascimento=date(2000, 1, 1),
            telefone="11999999999",
            endereco="Rua Teste, 123",
            ativo=True,
            criado_por="sistema"
        )
        
        # Tentar adicionar (mas não commitar)
        session.add(aluno_teste)
        session.flush()  # Força a execução da query sem commit
        
        print(f"✅ Aluno de teste criado com ID: {aluno_teste.id}")
        
        # Rollback para não salvar o teste
        session.rollback()
        session.close()
        
        print("✅ Teste de cadastro simulado bem-sucedido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no cadastro simulado: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = testar_models()
    success2 = testar_cadastro_simulado()
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram! A conexão está funcionando.")
    else:
        print("\n❌ Alguns testes falharam.")