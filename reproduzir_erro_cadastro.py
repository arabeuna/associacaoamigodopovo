#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import threading
import time

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos da aplicação
try:
    from database_integration import DatabaseIntegration
    from models import SessionLocal, Aluno
    print("✅ Módulos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

# Criar instância da integração do banco
db_integration = DatabaseIntegration()

def simular_cadastro_concorrente():
    """Simula múltiplos cadastros simultâneos para reproduzir o erro"""
    def cadastrar_aluno(thread_id):
        try:
            print(f"[Thread {thread_id}] Iniciando cadastro...")
            
            dados_aluno = {
                'nome': f'Teste Concorrente {thread_id}',
                'telefone': f'119999{thread_id:04d}',
                'endereco': f'Rua Teste {thread_id}, 123',
                'email': f'teste{thread_id}@email.com',
                'data_nascimento': '1990-01-01',
                'titulo_eleitor': f'{thread_id:011d}0',
                'atividade': 'Natação',
                'turma': '',
                'observacoes': f'Teste thread {thread_id}'
            }
            
            # Tentar salvar usando a função da aplicação
            resultado = db_integration.salvar_aluno_db(dados_aluno)
            
            if resultado['success']:
                print(f"[Thread {thread_id}] ✅ Cadastro bem-sucedido: {resultado['message']}")
            else:
                print(f"[Thread {thread_id}] ❌ Erro no cadastro: {resultado['message']}")
                
        except Exception as e:
            print(f"[Thread {thread_id}] ❌ Exceção durante cadastro: {e}")
            print(f"[Thread {thread_id}] Tipo da exceção: {type(e).__name__}")
            
            # Verificar se é o erro específico do PostgreSQL
            if 'psycopg2.OperationalError' in str(e) or 'connection refused' in str(e).lower():
                print(f"[Thread {thread_id}] 🎯 ERRO REPRODUZIDO! Este é o erro reportado pelo usuário.")
                return False
    
    print("=== Teste de Cadastros Concorrentes ===")
    threads = []
    
    # Criar múltiplas threads para simular cadastros simultâneos
    for i in range(5):
        thread = threading.Thread(target=cadastrar_aluno, args=(i+1,))
        threads.append(thread)
    
    # Iniciar todas as threads
    for thread in threads:
        thread.start()
        time.sleep(0.1)  # Pequeno delay entre threads
    
    # Aguardar todas as threads terminarem
    for thread in threads:
        thread.join()
    
    print("=== Teste de cadastros concorrentes finalizado ===")

def testar_pool_conexoes():
    """Testa o esgotamento do pool de conexões"""
    print("\n=== Teste de Pool de Conexões ===")
    
    sessions = []
    try:
        # Criar muitas sessões para esgotar o pool
        for i in range(20):
            session = SessionLocal()
            sessions.append(session)
            print(f"Sessão {i+1} criada")
            
            # Tentar fazer uma query simples
            try:
                result = session.execute("SELECT 1")
                print(f"Sessão {i+1}: Query executada com sucesso")
            except Exception as e:
                print(f"Sessão {i+1}: ❌ Erro na query: {e}")
                if 'connection refused' in str(e).lower():
                    print(f"🎯 ERRO REPRODUZIDO na sessão {i+1}!")
                    break
    
    except Exception as e:
        print(f"❌ Erro ao criar sessões: {e}")
        if 'connection refused' in str(e).lower():
            print("🎯 ERRO REPRODUZIDO durante criação de sessões!")
    
    finally:
        # Fechar todas as sessões
        for i, session in enumerate(sessions):
            try:
                session.close()
                print(f"Sessão {i+1} fechada")
            except:
                pass

def testar_transacao_longa():
    """Testa transações longas que podem causar timeout"""
    print("\n=== Teste de Transação Longa ===")
    
    session = SessionLocal()
    try:
        # Iniciar uma transação
        session.begin()
        print("Transação iniciada")
        
        # Simular operação longa
        print("Simulando operação longa (10 segundos)...")
        time.sleep(10)
        
        # Tentar fazer uma operação após o delay
        dados_aluno = {
            'nome': 'Teste Transação Longa',
            'telefone': '11888777666',
            'endereco': 'Rua Transação, 456',
            'email': 'transacao@email.com',
            'data_nascimento': '1985-05-15',
            'titulo_eleitor': '99988877766',
            'atividade': 'Natação',
            'observacoes': 'Teste de transação longa'
        }
        
        resultado = db_integration.salvar_aluno_db(dados_aluno)
        
        if resultado['success']:
            print("✅ Transação longa bem-sucedida")
        else:
            print(f"❌ Erro na transação longa: {resultado['message']}")
            if 'connection refused' in resultado['message'].lower():
                print("🎯 ERRO REPRODUZIDO em transação longa!")
        
        session.commit()
        
    except Exception as e:
        print(f"❌ Exceção em transação longa: {e}")
        if 'connection refused' in str(e).lower():
            print("🎯 ERRO REPRODUZIDO em transação longa!")
        session.rollback()
    
    finally:
        session.close()

if __name__ == "__main__":
    print("🔍 REPRODUÇÃO DO ERRO DE CADASTRO")
    print("=" * 60)
    
    # Teste 1: Cadastros concorrentes
    simular_cadastro_concorrente()
    
    # Teste 2: Pool de conexões
    testar_pool_conexoes()
    
    # Teste 3: Transação longa
    testar_transacao_longa()
    
    print("\n" + "=" * 60)
    print("🏁 Testes de reprodução finalizados")
    print("Se o erro não foi reproduzido, pode ser um problema intermitente")
    print("ou relacionado a condições específicas de uso.")