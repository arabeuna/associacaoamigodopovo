#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def debug_exclusao():
    """Debug detalhado da funcionalidade de exclusão"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        print("🔍 DEBUG DETALHADO DA EXCLUSÃO")
        print("=" * 40)
        
        # 1. Fazer login
        print("🔐 Fazendo login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
        else:
            print(f"❌ Falha no login: {response.status_code}")
            return False
        
        # 2. Testar exclusão com ID 1 e mostrar resposta completa
        aluno_id = 1
        print(f"\n🗑️ Testando exclusão do aluno ID: {aluno_id}")
        
        response = session.delete(f"{base_url}/excluir_aluno/{aluno_id}")
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        print(f"Conteúdo bruto da resposta: {repr(response.text)}")
        print(f"Conteúdo da resposta (primeiros 500 chars): {response.text[:500]}")
        
        # Tentar diferentes formas de interpretar a resposta
        try:
            result = response.json()
            print(f"✅ JSON válido: {result}")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            print("Tentando interpretar como HTML...")
            if '<html' in response.text.lower():
                print("📄 Resposta parece ser HTML (provavelmente uma página de erro ou redirecionamento)")
            else:
                print("📝 Resposta não é HTML nem JSON")
        
        # 3. Testar com método POST também
        print(f"\n🔄 Testando com método POST...")
        response = session.post(f"{base_url}/excluir_aluno/{aluno_id}")
        
        print(f"Status da resposta POST: {response.status_code}")
        print(f"Conteúdo da resposta POST (primeiros 200 chars): {response.text[:200]}")
        
        try:
            result = response.json()
            print(f"✅ JSON válido (POST): {result}")
        except json.JSONDecodeError:
            print("❌ Resposta POST também não é JSON válido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o debug: {e}")
        return False

if __name__ == "__main__":
    debug_exclusao()