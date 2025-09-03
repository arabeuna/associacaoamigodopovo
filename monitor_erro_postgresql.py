#!/usr/bin/env python3
"""
Script de Monitoramento para Capturar Erros de Conexão PostgreSQL
Este script monitora a aplicação e captura erros intermitentes de conexão
"""

import os
import sys
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_postgresql.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_integration import DatabaseIntegration
    from models import SessionLocal, engine
    import psycopg2
    from sqlalchemy import text
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

class PostgreSQLMonitor:
    """Monitor para capturar erros de conexão PostgreSQL"""
    
    def __init__(self):
        self.db_integration = DatabaseIntegration()
        self.error_count = 0
        self.success_count = 0
        self.monitoring = True
        
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com PostgreSQL"""
        try:
            session = SessionLocal()
            result = session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            session.close()
            
            return {
                'success': True,
                'message': f'Conexão OK - {version[:50]}...',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = str(e)
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat(),
                'is_connection_refused': 'connection refused' in error_msg.lower()
            }
    
    def test_cadastro_aluno(self) -> Dict[str, Any]:
        """Testa o cadastro de um aluno"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dados_aluno = {
                'nome': f'Monitor Test {timestamp}',
                'telefone': f'11{timestamp[-8:]}',
                'endereco': f'Rua Monitor, {timestamp[-3:]}',
                'email': f'monitor.{timestamp}@test.com',
                'data_nascimento': '1990-01-01',
                'titulo_eleitor': f'{timestamp[-11:]}',
                'atividade': 'Natação',
                'observacoes': f'Teste de monitoramento - {timestamp}'
            }
            
            resultado = self.db_integration.salvar_aluno_db(dados_aluno)
            
            if isinstance(resultado, dict) and resultado.get('success'):
                return {
                    'success': True,
                    'message': 'Cadastro realizado com sucesso',
                    'aluno_id': resultado.get('aluno_id'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': str(resultado),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = str(e)
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat(),
                'is_connection_refused': 'connection refused' in error_msg.lower()
            }
    
    def monitor_continuous(self, interval_seconds: int = 30):
        """Monitora continuamente a conexão PostgreSQL"""
        logger.info(f"🔍 Iniciando monitoramento contínuo (intervalo: {interval_seconds}s)")
        logger.info("Pressione Ctrl+C para parar o monitoramento")
        
        try:
            while self.monitoring:
                # Teste de conexão básica
                conn_result = self.test_connection()
                
                if conn_result['success']:
                    self.success_count += 1
                    logger.info(f"✅ Conexão OK ({self.success_count}) - {conn_result['message']}")
                else:
                    self.error_count += 1
                    logger.error(f"❌ ERRO DE CONEXÃO ({self.error_count}) - {conn_result['error']}")
                    
                    if conn_result.get('is_connection_refused'):
                        logger.critical("🎯 ERRO REPRODUZIDO! Connection refused detectado!")
                        self.log_detailed_error(conn_result)
                
                # Teste de cadastro (a cada 5 ciclos)
                if self.success_count % 5 == 0 and conn_result['success']:
                    cadastro_result = self.test_cadastro_aluno()
                    
                    if cadastro_result['success']:
                        logger.info(f"✅ Teste de cadastro OK - ID: {cadastro_result.get('aluno_id')}")
                    else:
                        logger.error(f"❌ ERRO NO CADASTRO - {cadastro_result['error']}")
                        
                        if cadastro_result.get('is_connection_refused'):
                            logger.critical("🎯 ERRO REPRODUZIDO NO CADASTRO! Connection refused detectado!")
                            self.log_detailed_error(cadastro_result)
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoramento interrompido pelo usuário")
            self.monitoring = False
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
    
    def log_detailed_error(self, error_info: Dict[str, Any]):
        """Registra detalhes do erro para análise"""
        error_file = f"erro_postgresql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write("=== ERRO DE CONEXÃO POSTGRESQL CAPTURADO ===\n")
            f.write(f"Timestamp: {error_info['timestamp']}\n")
            f.write(f"Tipo do erro: {error_info.get('error_type', 'N/A')}\n")
            f.write(f"Mensagem: {error_info['error']}\n")
            f.write(f"Connection refused: {error_info.get('is_connection_refused', False)}\n")
            f.write("\n=== INFORMAÇÕES DO SISTEMA ===\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Diretório: {os.getcwd()}\n")
            
            # Tentar obter informações do PostgreSQL
            try:
                import subprocess
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
                postgres_connections = [line for line in result.stdout.split('\n') if ':5432' in line]
                f.write(f"\nConexões PostgreSQL ativas:\n")
                for conn in postgres_connections[:10]:  # Limitar a 10 linhas
                    f.write(f"  {conn.strip()}\n")
            except:
                f.write("\nNão foi possível obter informações de conexão\n")
        
        logger.info(f"📝 Detalhes do erro salvos em: {error_file}")
    
    def monitor_stress_test(self, num_threads: int = 10, duration_seconds: int = 60):
        """Executa um teste de stress para provocar o erro"""
        logger.info(f"🔥 Iniciando teste de stress ({num_threads} threads por {duration_seconds}s)")
        
        def stress_worker(thread_id: int):
            start_time = time.time()
            operations = 0
            
            while time.time() - start_time < duration_seconds:
                try:
                    # Alternar entre teste de conexão e cadastro
                    if operations % 2 == 0:
                        result = self.test_connection()
                    else:
                        result = self.test_cadastro_aluno()
                    
                    operations += 1
                    
                    if not result['success'] and result.get('is_connection_refused'):
                        logger.critical(f"🎯 [Thread {thread_id}] ERRO REPRODUZIDO! Operação {operations}")
                        self.log_detailed_error(result)
                    
                    time.sleep(0.1)  # Pequeno delay entre operações
                    
                except Exception as e:
                    logger.error(f"[Thread {thread_id}] Erro na operação {operations}: {e}")
            
            logger.info(f"[Thread {thread_id}] Finalizou com {operations} operações")
        
        # Criar e iniciar threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=stress_worker, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem
        for thread in threads:
            thread.join()
        
        logger.info("🏁 Teste de stress finalizado")

def main():
    """Função principal"""
    monitor = PostgreSQLMonitor()
    
    print("🔍 MONITOR DE ERRO POSTGRESQL")
    print("=" * 50)
    print("Opções:")
    print("1. Monitoramento contínuo (padrão)")
    print("2. Teste de stress")
    print("3. Teste único")
    
    try:
        opcao = input("\nEscolha uma opção (1-3) [1]: ").strip() or "1"
        
        if opcao == "1":
            interval = input("Intervalo em segundos [30]: ").strip() or "30"
            monitor.monitor_continuous(int(interval))
        
        elif opcao == "2":
            threads = input("Número de threads [10]: ").strip() or "10"
            duration = input("Duração em segundos [60]: ").strip() or "60"
            monitor.monitor_stress_test(int(threads), int(duration))
        
        elif opcao == "3":
            print("\n=== Teste de Conexão ===")
            conn_result = monitor.test_connection()
            print(f"Resultado: {conn_result}")
            
            print("\n=== Teste de Cadastro ===")
            cadastro_result = monitor.test_cadastro_aluno()
            print(f"Resultado: {cadastro_result}")
        
        else:
            print("Opção inválida")
    
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido")
    except Exception as e:
        logger.error(f"Erro no programa principal: {e}")

if __name__ == "__main__":
    main()