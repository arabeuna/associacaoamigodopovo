#!/usr/bin/env python3
"""
Console de Debug para Academia Amigo do Povo
Permite monitorar logs em tempo real e executar testes
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from threading import Thread
import subprocess

class DebugConsole:
    def __init__(self):
        self.server_url = "http://localhost:5000"
        self.running = True
        self.log_file = None
        
    def clear_screen(self):
        """Limpa a tela do console"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Imprime o cabeçalho do console"""
        print("="*60)
        print("🔧 CONSOLE DE DEBUG - ACADEMIA AMIGO DO POVO")
        print("="*60)
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 🌐 {self.server_url}")
        print("-"*60)
        
    def show_menu(self):
        """Mostra o menu principal"""
        print("\n📋 OPÇÕES DISPONÍVEIS:")
        print("1. 🔍 Testar cadastro de aluno")
        print("2. 📊 Verificar status do servidor")
        print("3. 🗄️ Testar conexão com banco")
        print("4. 📝 Monitorar logs em tempo real")
        print("5. 🧪 Executar teste completo")
        print("6. 📋 Listar alunos do banco")
        print("7. 🔄 Reiniciar servidor")
        print("0. ❌ Sair")
        print("-"*60)
        
    def test_server_status(self):
        """Testa se o servidor está rodando"""
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor está rodando normalmente")
                return True
            else:
                print(f"⚠️ Servidor respondeu com status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Servidor não está rodando ou não está acessível")
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar com servidor: {e}")
            return False
            
    def test_database_connection(self):
        """Testa a conexão com o banco de dados"""
        try:
            # Importar módulos do sistema
            sys.path.append('.')
            from models import SessionLocal, Aluno
            
            db = SessionLocal()
            try:
                # Tentar fazer uma consulta simples
                count = db.query(Aluno).count()
                print(f"✅ Conexão com banco OK - {count} alunos encontrados")
                return True
            finally:
                db.close()
        except Exception as e:
            print(f"❌ Erro na conexão com banco: {e}")
            return False
            
    def test_student_registration(self):
        """Testa o cadastro de um aluno"""
        print("\n🧪 TESTE DE CADASTRO DE ALUNO")
        print("-"*40)
        
        # Dados de teste
        test_data = {
            'nome': f'Teste Debug {datetime.now().strftime("%H%M%S")}',
            'telefone': '11999999999',
            'email': 'teste@debug.com',
            'endereco': 'Rua de Teste, 123',
            'data_nascimento': '1990-01-01',
            'atividade': 'Futebol',
            'turma': 'Manhã',
            'status': 'Ativo',
            'observacoes': 'Cadastro de teste via console debug'
        }
        
        print(f"📝 Dados do teste: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        try:
            # Fazer login primeiro (se necessário)
            session = requests.Session()
            
            # Tentar cadastrar
            response = session.post(
                f"{self.server_url}/cadastrar_aluno",
                data=test_data,
                timeout=10
            )
            
            print(f"\n📡 Status da resposta: {response.status_code}")
            print(f"📄 Conteúdo da resposta: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print("✅ Cadastro realizado com sucesso!")
                        print(f"📊 Mensagem: {result.get('message')}")
                    else:
                        print("❌ Falha no cadastro")
                        print(f"📊 Erro: {result.get('message')}")
                except json.JSONDecodeError:
                    print("⚠️ Resposta não é JSON válido")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            
    def list_students(self):
        """Lista alunos do banco de dados"""
        try:
            sys.path.append('.')
            from models import SessionLocal, Aluno, Atividade, Turma
            
            db = SessionLocal()
            try:
                alunos = db.query(Aluno).filter(Aluno.ativo == True).limit(10).all()
                
                print(f"\n📋 ÚLTIMOS 10 ALUNOS CADASTRADOS:")
                print("-"*60)
                
                for aluno in alunos:
                    atividade_nome = aluno.atividade.nome if aluno.atividade else 'N/A'
                    turma_nome = aluno.turma.nome if aluno.turma else 'N/A'
                    
                    print(f"ID: {aluno.id} | {aluno.nome}")
                    print(f"   📞 {aluno.telefone} | 🎯 {atividade_nome} | 📅 {turma_nome}")
                    print(f"   📅 Cadastro: {aluno.data_cadastro}")
                    print("-"*40)
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Erro ao listar alunos: {e}")
            
    def monitor_logs(self):
        """Monitora logs em tempo real"""
        print("\n📝 MONITORAMENTO DE LOGS (Ctrl+C para parar)")
        print("-"*50)
        
        try:
            # Simular monitoramento de logs
            # Em um ambiente real, você poderia ler um arquivo de log
            print("🔍 Aguardando atividade no servidor...")
            print("💡 Dica: Execute ações no sistema para ver os logs aqui")
            
            while True:
                time.sleep(1)
                # Aqui você poderia implementar leitura de arquivo de log real
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido")
            
    def run_complete_test(self):
        """Executa um teste completo do sistema"""
        print("\n🧪 EXECUTANDO TESTE COMPLETO")
        print("="*40)
        
        tests = [
            ("Servidor", self.test_server_status),
            ("Banco de Dados", self.test_database_connection),
            ("Cadastro de Aluno", self.test_student_registration)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testando {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Erro no teste {test_name}: {e}")
                results.append((test_name, False))
                
        # Resumo dos resultados
        print("\n📊 RESUMO DOS TESTES:")
        print("-"*30)
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name}: {status}")
            
    def restart_server(self):
        """Reinicia o servidor (simulado)"""
        print("\n🔄 REINICIAR SERVIDOR")
        print("⚠️ Esta função requer implementação específica")
        print("💡 Dica: Use Ctrl+C no terminal do servidor e execute 'py app.py' novamente")
        
    def run(self):
        """Executa o console principal"""
        while self.running:
            self.clear_screen()
            self.print_header()
            self.show_menu()
            
            try:
                choice = input("\n🎯 Escolha uma opção: ").strip()
                
                if choice == '0':
                    print("\n👋 Saindo do console de debug...")
                    self.running = False
                elif choice == '1':
                    self.test_student_registration()
                elif choice == '2':
                    self.test_server_status()
                elif choice == '3':
                    self.test_database_connection()
                elif choice == '4':
                    self.monitor_logs()
                elif choice == '5':
                    self.run_complete_test()
                elif choice == '6':
                    self.list_students()
                elif choice == '7':
                    self.restart_server()
                else:
                    print("\n❌ Opção inválida!")
                    
                if choice != '0':
                    input("\n⏸️ Pressione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Saindo do console de debug...")
                self.running = False
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                input("\n⏸️ Pressione Enter para continuar...")

if __name__ == "__main__":
    console = DebugConsole()
    console.run()