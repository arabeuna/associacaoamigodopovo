#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def testar_login_e_busca():
    """Testa login e busca na interface web"""
    print("🌐 Testando interface web de busca...")
    
    # URL base
    base_url = "http://127.0.0.1:5000"
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Configurar headers para simular navegador
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        # 1. Acessar página de login
        print("📄 Acessando página de login...")
        response = session.get(f"{base_url}/login")
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar login: {response.status_code}")
            return
        
        print("✅ Página de login acessada com sucesso!")
        
        # 2. Fazer login
        print("🔐 Fazendo login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': base_url,
            'Referer': f"{base_url}/login"
        }
        
        response = session.post(f"{base_url}/login", data=login_data, headers=login_headers)
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            return
        
        print("✅ Login realizado com sucesso!")
        
        # 3. Acessar página de alunos
        print("📋 Acessando página de alunos...")
        response = session.get(f"{base_url}/alunos")
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar alunos: {response.status_code}")
            return
        
        print("✅ Página de alunos acessada com sucesso!")
        
        # 4. Testar busca de alunos via AJAX
        print("🔍 Testando busca de alunos via AJAX...")
        
        # Configurar headers para requisição AJAX
        ajax_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        
        response = session.get(f"{base_url}/buscar_alunos", headers=ajax_headers)
        
        print(f"📊 Status da busca: {response.status_code}")
        print(f"📊 Headers da resposta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                print(f"✅ Busca bem-sucedida! Encontrados {len(dados)} alunos")
                
                # Mostrar primeiros 3 alunos
                for i, aluno in enumerate(dados[:3]):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                
                if len(dados) > 3:
                    print(f"   ... e mais {len(dados) - 3} alunos")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"   Resposta: {response.text[:500]}...")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"   Resposta: {response.text[:500]}...")
        
        # 5. Testar busca com filtro
        print("\n🔍 Testando busca com filtro 'joão'...")
        response = session.get(f"{base_url}/buscar_alunos?termo=joão", headers=ajax_headers)
        
        if response.status_code == 200:
            try:
                dados = response.json()
                print(f"✅ Busca com filtro bem-sucedida! Encontrados {len(dados)} alunos")
                
                for i, aluno in enumerate(dados[:3]):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON da busca filtrada: {e}")
        else:
            print(f"❌ Erro na busca com filtro: {response.status_code}")
        
        print("\n✅ Teste da interface web concluído!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    testar_login_e_busca()
