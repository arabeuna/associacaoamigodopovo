#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se a interface local está funcionando corretamente
e se os alunos aparecem na página de alunos
"""

import requests
import json
from datetime import datetime
import time

print("🧪 TESTE DA INTERFACE LOCAL")
print("="*50)

# URL base da aplicação local
BASE_URL = "http://localhost:5000"

def testar_conexao():
    """Testa se a aplicação está rodando"""
    try:
        print("🔌 Testando conexão com a aplicação...")
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Aplicação está rodando")
            return True
        else:
            print(f"❌ Aplicação retornou status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à aplicação")
        print("💡 Certifique-se de que 'python app.py' está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def testar_login():
    """Testa o login na aplicação"""
    try:
        print("\n🔐 Testando login...")
        session = requests.Session()
        
        # Fazer login como admin
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{BASE_URL}/login", data=login_data, timeout=10)
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print("✅ Login realizado com sucesso")
            return session
        else:
            print(f"❌ Falha no login. Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def testar_dashboard(session):
    """Testa se o dashboard carrega corretamente"""
    try:
        print("\n📊 Testando dashboard...")
        response = session.get(f"{BASE_URL}/dashboard", timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard carregado com sucesso")
            
            # Verificar se há dados no HTML
            html_content = response.text
            if "Total de Alunos" in html_content:
                print("✅ Dashboard contém seção de estatísticas")
                
                # Tentar extrair número de alunos
                import re
                alunos_match = re.search(r'Total de Alunos[^\d]*(\d+)', html_content)
                if alunos_match:
                    num_alunos = alunos_match.group(1)
                    print(f"📊 Número de alunos no dashboard: {num_alunos}")
                    return int(num_alunos)
                else:
                    print("⚠️  Não foi possível extrair número de alunos")
            else:
                print("⚠️  Dashboard não contém estatísticas de alunos")
                
        else:
            print(f"❌ Falha ao carregar dashboard. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        
    return 0

def testar_pagina_alunos(session):
    """Testa se a página de alunos carrega e mostra os dados"""
    try:
        print("\n👥 Testando página de alunos...")
        response = session.get(f"{BASE_URL}/alunos", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de alunos carregada com sucesso")
            
            html_content = response.text
            
            # Verificar elementos importantes
            checks = [
                ("Alunos Cadastrados", "título da página"),
                ("Total de Alunos", "contador de alunos"),
                ("table", "tabela de alunos"),
                ("tbody", "corpo da tabela"),
                ("Buscar Alunos", "campo de busca")
            ]
            
            for check, desc in checks:
                if check in html_content:
                    print(f"✅ {desc} encontrado")
                else:
                    print(f"❌ {desc} NÃO encontrado")
            
            # Contar linhas de alunos na tabela
            import re
            tr_matches = re.findall(r'<tr[^>]*data-aluno', html_content)
            num_linhas = len(tr_matches)
            print(f"📊 Linhas de alunos na tabela: {num_linhas}")
            
            # Verificar se há mensagem de "nenhum aluno"
            if "Nenhum aluno cadastrado" in html_content or "não foram encontrados" in html_content:
                print("❌ Página mostra mensagem de 'nenhum aluno'")
                return 0
            else:
                print("✅ Página não mostra mensagem de 'nenhum aluno'")
                return num_linhas
                
        else:
            print(f"❌ Falha ao carregar página de alunos. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar página de alunos: {e}")
        
    return 0

def testar_api_buscar_alunos(session):
    """Testa a API de busca de alunos"""
    try:
        print("\n🔍 Testando API de busca de alunos...")
        response = session.get(f"{BASE_URL}/buscar_alunos", timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ API retornou {len(data)} alunos")
                    
                    if len(data) > 0:
                        # Mostrar exemplo do primeiro aluno
                        primeiro_aluno = data[0]
                        nome = primeiro_aluno.get('nome', 'N/A')
                        atividade = primeiro_aluno.get('atividade', 'N/A')
                        ativo = primeiro_aluno.get('ativo', 'N/A')
                        print(f"📋 Exemplo: {nome} - {atividade} - Ativo: {ativo}")
                        
                        # Contar alunos ativos
                        ativos = sum(1 for aluno in data if aluno.get('ativo', False))
                        print(f"✅ Alunos ativos: {ativos}/{len(data)}")
                        
                        return len(data)
                    else:
                        print("⚠️  API retornou lista vazia")
                        return 0
                else:
                    print(f"❌ API retornou formato inesperado: {type(data)}")
                    return 0
                    
            except json.JSONDecodeError:
                print("❌ Resposta da API não é JSON válido")
                return 0
        else:
            print(f"❌ Falha na API. Status: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return 0

def main():
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Aguardar um pouco para garantir que a aplicação esteja rodando
    print("⏳ Aguardando 3 segundos para garantir que a aplicação esteja pronta...")
    time.sleep(3)
    
    # Teste 1: Conexão
    if not testar_conexao():
        print("\n❌ FALHA: Aplicação não está rodando")
        print("💡 Execute 'python app.py' em outro terminal")
        return
    
    # Teste 2: Login
    session = testar_login()
    if not session:
        print("\n❌ FALHA: Não foi possível fazer login")
        return
    
    # Teste 3: Dashboard
    alunos_dashboard = testar_dashboard(session)
    
    # Teste 4: Página de alunos
    alunos_pagina = testar_pagina_alunos(session)
    
    # Teste 5: API de busca
    alunos_api = testar_api_buscar_alunos(session)
    
    # Resumo
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES")
    print("="*50)
    print(f"📊 Alunos no dashboard: {alunos_dashboard}")
    print(f"👥 Alunos na página: {alunos_pagina}")
    print(f"🔍 Alunos na API: {alunos_api}")
    
    if alunos_api > 0:
        print("\n🎉 SUCESSO: A aplicação está funcionando!")
        print(f"✅ {alunos_api} alunos foram encontrados")
        
        if alunos_api == 315:
            print("🎯 PERFEITO: Todos os 315 alunos estão sendo exibidos")
        else:
            print(f"⚠️  ATENÇÃO: Esperado 315 alunos, encontrado {alunos_api}")
    else:
        print("\n❌ PROBLEMA: Nenhum aluno foi encontrado")
        print("🔍 Possíveis causas:")
        print("   - Problema na conexão com MongoDB")
        print("   - Filtros de usuário bloqueando dados")
        print("   - Erro na função obter_alunos_usuario()")
    
    print("\n" + "="*50)
    print("🏁 TESTE CONCLUÍDO")
    print("="*50)

if __name__ == "__main__":
    main()