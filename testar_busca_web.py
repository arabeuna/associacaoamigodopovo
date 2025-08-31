#!/usr/bin/env python3
"""
Script para testar a busca de alunos via web
"""
import requests
import json

def testar_busca_web():
    """Testa a busca de alunos via web"""
    print("🔍 Testando busca de alunos via web...")
    
    # URL base
    base_url = "http://127.0.0.1:5000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Configurar headers para simular um navegador real
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        # Primeiro verificar se conseguimos acessar a página inicial
        print("🌐 Verificando acesso à página inicial...")
        response = session.get(f"{base_url}/")
        print(f"Status inicial: {response.status_code}")
        
        # Fazer login
        print("\n📝 Fazendo login...")
        login_data = {
            'usuario': 'admin',
            'senha': 'admin123'
        }
        
        # Fazer login com headers específicos para POST
        login_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url,
            'Referer': f"{base_url}/login",
        }
        
        response = session.post(f"{base_url}/login", data=login_data, headers=login_headers, allow_redirects=True)
        
        print(f"Login Status: {response.status_code}")
        print(f"Login URL: {response.url}")
        print(f"Session Cookies: {dict(session.cookies)}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Verificar se fomos redirecionados para o dashboard
        if "dashboard" in response.url:
            print("✅ Login bem-sucedido - redirecionado para dashboard!")
        else:
            print("⚠️ Login pode não ter funcionado - não redirecionado para dashboard")
            print(f"Conteúdo da resposta: {response.text[:500]}...")
        
        # Testar acesso ao dashboard
        print("\n🏠 Testando acesso ao dashboard...")
        response = session.get(f"{base_url}/dashboard")
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard acessível!")
        else:
            print("❌ Dashboard não acessível!")
            print(f"Conteúdo: {response.text[:500]}...")
        
        # Testar busca vazia (todos os alunos)
        print("\n🔍 Testando busca vazia...")
        response = session.get(f"{base_url}/buscar_alunos")
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                if dados.get('success'):
                    print(f"✅ Busca vazia funcionando!")
                    print(f"   📊 Total de alunos: {dados.get('total_encontrado', 0)}")
                    
                    # Mostrar alguns alunos
                    alunos = dados.get('alunos', [])
                    if alunos:
                        print("   📋 Primeiros 3 alunos:")
                        for i, aluno in enumerate(alunos[:3]):
                            print(f"      {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                else:
                    print(f"❌ Erro na busca: {dados.get('message', 'Erro desconhecido')}")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"Resposta completa: {response.text[:500]}...")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text[:500]}...")
        
        # Testar busca com termo
        print("\n🔍 Testando busca por 'joão'...")
        response = session.get(f"{base_url}/buscar_alunos?termo=joão")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                if dados.get('success'):
                    print(f"✅ Busca por 'joão' funcionando!")
                    print(f"   📊 Total encontrado: {dados.get('total_encontrado', 0)}")
                    
                    # Mostrar alguns resultados
                    alunos = dados.get('alunos', [])
                    if alunos:
                        print("   📋 Resultados:")
                        for i, aluno in enumerate(alunos[:5]):
                            print(f"      {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                else:
                    print(f"❌ Erro na busca: {dados.get('message', 'Erro desconhecido')}")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o servidor está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_busca_web()
