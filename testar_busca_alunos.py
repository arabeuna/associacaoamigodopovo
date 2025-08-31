#!/usr/bin/env python3
"""
Script para testar a rota de busca de alunos
"""
import requests
import json

def testar_busca_alunos():
    """Testa a rota de busca de alunos"""
    print("🔍 Testando rota de busca de alunos...")
    
    # URL base
    base_url = "http://127.0.0.1:5000"
    
    # Primeiro fazer login
    print("📝 Fazendo login...")
    login_data = {
        'usuario': 'admin',
        'senha': 'admin123'
    }
    
    session = requests.Session()
    
    try:
        # Fazer login
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
        
        print(f"Login Status: {response.status_code}")
        print(f"Login URL: {response.url}")
        print(f"Session Cookies: {dict(session.cookies)}")
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso!")
            
            # Testar busca vazia (todos os alunos)
            print("\n🔍 Testando busca vazia...")
            response = session.get(f"{base_url}/buscar_alunos")
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    dados = response.json()
                    if dados.get('success'):
                        print(f"✅ Busca vazia funcionando!")
                        print(f"   📊 Total de alunos: {dados.get('total_encontrado', 0)}")
                    else:
                        print(f"❌ Erro na busca: {dados.get('message', 'Erro desconhecido')}")
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {e}")
                    print(f"Resposta completa: {response.text}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
            
        else:
            print(f"❌ Erro no login: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o servidor está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_busca_alunos()
