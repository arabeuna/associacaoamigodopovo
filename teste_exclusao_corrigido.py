#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def teste_exclusao_corrigido():
    """Teste corrigido da funcionalidade de exclusão de alunos"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        print("🧪 TESTE CORRIGIDO DE EXCLUSÃO DE ALUNO")
        print("=" * 40)
        
        # 1. Fazer login com os campos corretos
        print("🔐 Fazendo login...")
        login_data = {
            'usuario': 'admin',  # Campo correto
            'senha': 'admin123'  # Campo correto
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"Status do login: {response.status_code}")
        print(f"Cookies após login: {dict(session.cookies)}")
        
        if response.status_code == 302:  # Redirecionamento após login bem-sucedido
            print("✅ Login realizado com sucesso (redirecionamento)")
        elif response.status_code == 200:
            print("✅ Login realizado com sucesso")
        else:
            print(f"❌ Falha no login: {response.status_code}")
            return False
        
        # 2. Verificar se conseguimos acessar o dashboard (teste de autenticação)
        print("\n🏠 Testando acesso ao dashboard...")
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard acessível - autenticação funcionando")
        else:
            print(f"❌ Dashboard não acessível: {response.status_code}")
            return False
        
        # 3. Testar exclusão com diferentes IDs
        test_ids = [1, 2, 3, 5, 10, 15, 20]
        
        for aluno_id in test_ids:
            print(f"\n🗑️ Testando exclusão do aluno ID: {aluno_id}")
            
            # Fazer requisição DELETE
            response = session.delete(f"{base_url}/excluir_aluno/{aluno_id}")
            
            print(f"Status da resposta: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                # Verificar se a resposta é JSON
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        result = response.json()
                        if result.get('success'):
                            print(f"✅ Aluno {aluno_id} excluído com sucesso!")
                            print(f"   Mensagem: {result.get('message')}")
                            if result.get('frequencia_removida'):
                                print(f"   Registros de frequência removidos: {result.get('registros_removidos')}")
                            return True  # Sucesso!
                        else:
                            print(f"❌ Falha na exclusão: {result.get('message')}")
                    except json.JSONDecodeError:
                        print("❌ Resposta não é JSON válido")
                        print(f"   Primeiros 200 chars: {response.text[:200]}")
                else:
                    print("❌ Resposta não é JSON (Content-Type incorreto)")
                    if '<html' in response.text.lower():
                        print("   Resposta parece ser HTML (possível redirecionamento)")
                    print(f"   Primeiros 200 chars: {response.text[:200]}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
        
        print("\n⚠️ Nenhum dos IDs testados resultou em exclusão bem-sucedida")
        print("Isso pode indicar que não há alunos com esses IDs ou há outro problema")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_exclusao_corrigido()
    if sucesso:
        print("\n🎉 TESTE DE EXCLUSÃO PASSOU!")
        print("✅ A funcionalidade de exclusão está funcionando corretamente")
    else:
        print("\n⚠️ TESTE DE EXCLUSÃO NÃO PASSOU")
        print("❌ Pode haver problemas com a funcionalidade ou não há alunos para testar")