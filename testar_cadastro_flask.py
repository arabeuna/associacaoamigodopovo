#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from database_integration import get_db_integration
from models import SessionLocal, engine
from sqlalchemy import text

def testar_cadastro_via_database_integration():
    """Testa o cadastro usando a mesma função que a aplicação Flask usa"""
    try:
        print("=== Teste de Cadastro via Database Integration ===")
        
        # Obter instância do database integration (como a aplicação faz)
        db_integration = get_db_integration()
        
        # Dados de teste (simulando um cadastro real)
        dados_aluno = {
            'nome': 'Teste Cadastro Flask',
            'telefone': '11987654321',
            'endereco': 'Rua Teste Flask, 456',
            'email': 'teste.flask@email.com',
            'data_nascimento': '1995-05-15',
            'titulo_eleitor': '123456789012',
            'atividade': 'Natação',  # Assumindo que existe
            'turma': '',  # Pode ser vazio
            'observacoes': 'Teste de cadastro via Flask'
        }
        
        print(f"Tentando cadastrar: {dados_aluno['nome']}")
        
        # Tentar salvar usando o mesmo método da aplicação
        aluno_id = db_integration.salvar_aluno_db(dados_aluno)
        
        if aluno_id:
            print(f"✅ Aluno cadastrado com sucesso! ID: {aluno_id}")
            
            # Verificar se foi realmente salvo
            session = SessionLocal()
            result = session.execute(
                text("SELECT nome FROM alunos WHERE id = :id"),
                {"id": aluno_id}
            )
            aluno_verificacao = result.fetchone()
            session.close()
            
            if aluno_verificacao:
                print(f"✅ Verificação: Aluno '{aluno_verificacao[0]}' encontrado no banco")
                return True
            else:
                print("❌ Aluno não encontrado na verificação")
                return False
        else:
            print("❌ Falha no cadastro - ID não retornado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de cadastro: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def testar_pool_conexoes():
    """Testa o comportamento do pool de conexões"""
    try:
        print("\n=== Teste do Pool de Conexões ===")
        
        # Informações sobre o pool
        pool = engine.pool
        print(f"Tipo do pool: {type(pool).__name__}")
        print(f"Tamanho do pool: {pool.size()}")
        print(f"Conexões em uso: {pool.checkedin()}")
        print(f"Conexões disponíveis: {pool.checkedout()}")
        
        # Testar múltiplas conexões
        sessions = []
        for i in range(5):
            try:
                session = SessionLocal()
                result = session.execute(text("SELECT 1"))
                result.fetchone()
                sessions.append(session)
                print(f"✅ Conexão {i+1} estabelecida")
            except Exception as e:
                print(f"❌ Erro na conexão {i+1}: {e}")
                break
        
        # Fechar todas as sessões
        for session in sessions:
            session.close()
        
        print(f"✅ Teste do pool concluído - {len(sessions)} conexões testadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do pool: {e}")
        return False

def testar_configuracao_engine():
    """Testa a configuração do engine SQLAlchemy"""
    try:
        print("\n=== Teste da Configuração do Engine ===")
        
        print(f"URL do Engine: {engine.url}")
        print(f"Driver: {engine.url.drivername}")
        print(f"Host: {engine.url.host}")
        print(f"Port: {engine.url.port}")
        print(f"Database: {engine.url.database}")
        
        # Testar configurações do pool
        print(f"\nConfigurações do Pool:")
        print(f"Pool size: {getattr(engine.pool, '_pool_size', 'N/A')}")
        print(f"Max overflow: {getattr(engine.pool, '_max_overflow', 'N/A')}")
        print(f"Pool timeout: {getattr(engine.pool, '_timeout', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de configuração: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DE CADASTRO FLASK")
    print("=" * 50)
    
    success1 = testar_configuracao_engine()
    success2 = testar_pool_conexoes()
    success3 = testar_cadastro_via_database_integration()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("🎉 Todos os testes passaram! O sistema está funcionando.")
    else:
        print("❌ Alguns testes falharam - há problemas na configuração.")