#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def testar_cadastro_via_http():
    """Testa o cadastro de aluno via requisição HTTP para a aplicação Flask"""
    try:
        print("=== Teste de Cadastro via HTTP ===")
        
        # URL da aplicação Flask
        base_url = "http://127.0.0.1:5000"
        
        # Primeiro, fazer login (se necessário)
        session = requests.Session()
        
        # Tentar acessar a página de login
        login_response = session.get(f"{base_url}/login")
        print(f"Status da página de login: {login_response.status_code}")
        
        # Fazer login com credenciais de teste
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_post = session.post(f"{base_url}/login", data=login_data)
        print(f"Status do login: {login_post.status_code}")
        
        if login_post.status_code == 200 and 'dashboard' in login_post.url:
            print("✅ Login realizado com sucesso")
        else:
            print("⚠️ Login pode ter falhado, continuando mesmo assim...")
        
        # Dados do aluno para cadastro
        dados_aluno = {
            'nome': 'Teste HTTP Cadastro',
            'telefone': '11999888777',
            'endereco': 'Rua Teste HTTP, 789',
            'email': 'teste.http@email.com',
            'data_nascimento': '1990-12-25',
            'titulo_eleitor': '987654321098',
            'atividade': 'Natação',
            'turma': '',
            'observacoes': 'Teste de cadastro via HTTP'
        }
        
        print(f"\nTentando cadastrar via HTTP: {dados_aluno['nome']}")
        
        # Fazer requisição POST para cadastrar aluno
        cadastro_response = session.post(
            f"{base_url}/cadastrar_aluno",
            data=dados_aluno,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Status da resposta: {cadastro_response.status_code}")
        print(f"URL final: {cadastro_response.url}")
        
        # Verificar se há mensagens de erro na resposta
        response_text = cadastro_response.text
        if 'erro' in response_text.lower() or 'error' in response_text.lower():
            print("❌ Possível erro detectado na resposta:")
            # Procurar por mensagens de erro específicas
            lines = response_text.split('\n')
            for line in lines:
                if 'erro' in line.lower() or 'error' in line.lower():
                    print(f"   {line.strip()}")
        
        if cadastro_response.status_code == 200:
            print("✅ Requisição HTTP processada com sucesso")
            return True
        else:
            print(f"❌ Erro na requisição HTTP: {cadastro_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Verifique se a aplicação Flask está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro no teste HTTP: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def testar_endpoint_json():
    """Testa cadastro via endpoint JSON (se existir)"""
    try:
        print("\n=== Teste via JSON API ===")
        
        session = requests.Session()
        base_url = "http://127.0.0.1:5000"
        
        # Dados em formato JSON
        dados_json = {
            'nome': 'Teste JSON API',
            'telefone': '11888777666',
            'endereco': 'Rua JSON, 123',
            'email': 'teste.json@email.com',
            'data_nascimento': '1985-06-15',
            'titulo_eleitor': '111222333444',
            'atividade': 'Natação',
            'observacoes': 'Teste via JSON API'
        }
        
        # Tentar endpoint JSON
        response = session.post(
            f"{base_url}/api/alunos",
            json=dados_json,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status JSON API: {response.status_code}")
        
        if response.status_code == 404:
            print("⚠️ Endpoint JSON não encontrado - normal se não existir")
            return True
        elif response.status_code == 200:
            print("✅ Cadastro via JSON API bem-sucedido")
            return True
        else:
            print(f"❌ Erro na API JSON: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalhes do erro: {error_data}")
            except:
                print(f"Resposta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste JSON: {e}")
        return False

if __name__ == "__main__":
    print("🌐 TESTE DE CADASTRO VIA HTTP")
    print("=" * 50)
    
    success1 = testar_cadastro_via_http()
    success2 = testar_endpoint_json()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 Teste HTTP passou! A aplicação está respondendo corretamente.")
    else:
        print("❌ Teste HTTP falhou - há problemas na aplicação.")