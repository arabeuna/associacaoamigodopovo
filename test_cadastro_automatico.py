#!/usr/bin/env python3
"""
Teste Automático de Cadastro de Aluno com Login
Executa login e depois testa o cadastro de aluno
"""

import requests
import json
from datetime import datetime

def fazer_login(session, server_url):
    """Faz login no sistema"""
    print("🔐 FAZENDO LOGIN NO SISTEMA")
    print("-"*40)
    
    # Credenciais de admin
    login_data = {
        'usuario': 'admin',
        'senha': 'admin123'
    }
    
    try:
        # Fazer login
        response = session.post(
            f"{server_url}/login",
            data=login_data,
            timeout=10,
            allow_redirects=False
        )
        
        print(f"📡 Status do login: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        # Verificar se login foi bem-sucedido
        if response.status_code == 302:  # Redirecionamento após login
            print("✅ Login realizado com sucesso!")
            return True
        elif response.status_code == 200:
            # Verificar se há mensagem de erro na resposta
            if 'Usuário ou senha inválidos' in response.text:
                print("❌ Credenciais inválidas")
                return False
            else:
                print("✅ Login realizado com sucesso!")
                return True
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Conteúdo: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante login: {e}")
        return False

def test_student_registration_with_login():
    """Testa o cadastro de um aluno com login"""
    print("🧪 TESTE COMPLETO DE CADASTRO DE ALUNO")
    print("="*50)
    
    server_url = "http://localhost:5000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Fazer login primeiro
    if not fazer_login(session, server_url):
        print("\n❌ Não foi possível fazer login. Teste abortado.")
        return
    
    print("\n🧪 TESTANDO CADASTRO DE ALUNO")
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
        'status': 'Ativo',  # Campo correto do formulário
        'observacoes': 'Cadastro de teste automático com login'
    }
    
    print(f"📝 Dados do teste:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Tentar cadastrar
        print(f"\n📤 Enviando dados de cadastro...")
        response = session.post(
            f"{server_url}/cadastrar_aluno",
            data=test_data,
            timeout=10
        )
        
        print(f"\n📡 Status da resposta: {response.status_code}")
        print(f"📄 Headers da resposta: {dict(response.headers)}")
        print(f"📄 Conteúdo da resposta (primeiros 1000 chars): {response.text[:1000]}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n📊 Resposta JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('success'):
                    print("\n✅ CADASTRO REALIZADO COM SUCESSO!")
                    print(f"📊 Mensagem: {result.get('message')}")
                    if 'total_alunos' in result:
                        print(f"📊 Total de alunos: {result.get('total_alunos')}")
                else:
                    print("\n❌ FALHA NO CADASTRO")
                    print(f"📊 Erro: {result.get('message')}")
                    
            except json.JSONDecodeError as e:
                print(f"\n⚠️ Resposta não é JSON válido: {e}")
                print(f"📄 Conteúdo bruto: {response.text[:500]}")
                
                # Verificar se foi redirecionado para login
                if 'login' in response.text.lower():
                    print("\n⚠️ Parece que foi redirecionado para página de login")
                    print("💡 Possível problema com autenticação")
        else:
            print(f"\n❌ ERRO HTTP: {response.status_code}")
            print(f"📄 Conteúdo: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar com o servidor")
        print("💡 Verifique se o servidor está rodando em http://localhost:5000")
    except requests.exceptions.Timeout:
        print("\n❌ ERRO: Timeout na conexão")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()

def test_server_status():
    """Testa se o servidor está rodando"""
    print("\n🔍 TESTANDO STATUS DO SERVIDOR")
    print("-"*40)
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
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

def test_login_only():
    """Testa apenas o login"""
    print("\n🔐 TESTE ISOLADO DE LOGIN")
    print("-"*40)
    
    session = requests.Session()
    server_url = "http://localhost:5000"
    
    return fazer_login(session, server_url)

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE AUTOMÁTICO COM LOGIN")
    print("="*50)
    
    # Testar servidor primeiro
    if not test_server_status():
        print("\n❌ Não é possível continuar - servidor não está acessível")
        exit(1)
    
    # Testar login isoladamente
    print("\n" + "="*50)
    if not test_login_only():
        print("\n❌ Não é possível continuar - falha no login")
        exit(1)
    
    # Se tudo estiver OK, testar cadastro completo
    print("\n" + "="*50)
    test_student_registration_with_login()
    
    print("\n🏁 TESTE CONCLUÍDO")
    print("="*50)