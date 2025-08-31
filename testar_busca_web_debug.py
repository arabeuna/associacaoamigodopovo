#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de debug da interface web de busca
"""

import requests
import json

def testar_busca_web_debug():
    """Testa a interface web com debug detalhado"""
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    # Configurar headers para simular navegador
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    print("🌐 Testando interface web de busca (debug)...")
    
    # Teste 1: Verificar se o servidor está rodando
    print("\n==================================================")
    print("TESTE 1: Verificar servidor")
    print("==================================================")
    
    try:
        response = session.get(f"{base_url}/")
        print(f"📊 Status da página inicial: {response.status_code}")
        print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
        print(f"📏 Tamanho da resposta: {len(response.text)} caracteres")
        
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
        else:
            print("❌ Servidor não está respondendo corretamente")
            return
            
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return
    
    # Teste 2: Tentar login
    print("\n==================================================")
    print("TESTE 2: Tentar login")
    print("==================================================")
    
    login_data = {
        'usuario': 'admin_master',
        'senha': 'master123'
    }
    
    try:
        response = session.post(f"{base_url}/login", data=login_data)
        print(f"📊 Status do login: {response.status_code}")
        print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
        print(f"🍪 Cookies após login: {dict(session.cookies)}")
        
        if response.status_code == 302:  # Redirect após login
            print("✅ Login parece ter sido bem-sucedido (redirect)")
        else:
            print("⚠️ Login pode ter falhado")
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
    
    # Teste 3: Testar busca sem filtro
    print("\n==================================================")
    print("TESTE 3: Testar busca sem filtro")
    print("==================================================")
    
    try:
        response = session.get(f"{base_url}/buscar_alunos")
        print(f"📊 Status da busca: {response.status_code}")
        print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
        print(f"📏 Tamanho da resposta: {len(response.text)} caracteres")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Resposta JSON válida!")
                print(f"📊 Sucesso: {data.get('success', 'N/A')}")
                print(f"👥 Total de alunos: {data.get('total_encontrado', 'N/A')}")
                print(f"🔍 Termo de busca: {data.get('termo_busca', 'N/A')}")
                
                if data.get('alunos'):
                    print(f"📋 Primeiros 3 alunos:")
                    for i, aluno in enumerate(data['alunos'][:3]):
                        print(f"  {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                else:
                    print("⚠️ Nenhum aluno retornado")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Primeiros 200 caracteres da resposta:")
                print(response.text[:200])
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
    
    # Teste 4: Testar busca com filtro
    print("\n==================================================")
    print("TESTE 4: Testar busca com filtro 'joão'")
    print("==================================================")
    
    try:
        response = session.get(f"{base_url}/buscar_alunos?termo=joão")
        print(f"📊 Status da busca: {response.status_code}")
        print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Resposta JSON válida!")
                print(f"📊 Sucesso: {data.get('success', 'N/A')}")
                print(f"👥 Total de alunos: {data.get('total_encontrado', 'N/A')}")
                print(f"🔍 Termo de busca: {data.get('termo_busca', 'N/A')}")
                
                if data.get('alunos'):
                    print(f"📋 Alunos encontrados:")
                    for i, aluno in enumerate(data['alunos']):
                        print(f"  {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                else:
                    print("⚠️ Nenhum aluno encontrado com o filtro")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Primeiros 200 caracteres da resposta:")
                print(response.text[:200])
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
    
    # Teste 5: Testar modo de teste
    print("\n==================================================")
    print("TESTE 5: Testar modo de teste (bypass sessão)")
    print("==================================================")
    
    try:
        response = session.get(f"{base_url}/buscar_alunos?teste=true")
        print(f"📊 Status da busca (modo teste): {response.status_code}")
        print(f"📄 Tipo de conteúdo: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Resposta JSON válida!")
                print(f"📊 Sucesso: {data.get('success', 'N/A')}")
                print(f"👥 Total de alunos: {data.get('total_encontrado', 'N/A')}")
                print(f"🔍 Termo de busca: {data.get('termo_busca', 'N/A')}")
                
                if data.get('alunos'):
                    print(f"📋 Primeiros 3 alunos:")
                    for i, aluno in enumerate(data['alunos'][:3]):
                        print(f"  {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                else:
                    print("⚠️ Nenhum aluno retornado no modo teste")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"📄 Primeiros 200 caracteres da resposta:")
                print(response.text[:200])
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro na busca (modo teste): {e}")
    
    print("\n✅ Teste de debug concluído!")

if __name__ == "__main__":
    testar_busca_web_debug()
