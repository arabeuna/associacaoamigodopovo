#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def teste_exclusao_final():
    """Teste final da funcionalidade de exclusão de alunos"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        print("🧪 TESTE FINAL DE EXCLUSÃO DE ALUNO")
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
        
        # 2. Listar alguns alunos para encontrar um ID válido
        print("\n📋 Buscando alunos disponíveis...")
        response = session.get(f"{base_url}/alunos")
        if response.status_code == 200:
            print("✅ Lista de alunos obtida")
            # Vamos tentar com alguns IDs comuns
            test_ids = [1, 2, 3, 5, 10]
        else:
            print(f"❌ Erro ao obter lista de alunos: {response.status_code}")
            return False
        
        # 3. Testar exclusão com diferentes IDs
        for aluno_id in test_ids:
            print(f"\n🗑️ Testando exclusão do aluno ID: {aluno_id}")
            
            # Fazer requisição DELETE
            response = session.delete(f"{base_url}/excluir_aluno/{aluno_id}")
            
            print(f"Status da resposta: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Aluno {aluno_id} excluído com sucesso!")
                        print(f"   Mensagem: {result.get('message')}")
                        if result.get('frequencia_removida'):
                            print(f"   Registros de frequência removidos: {result.get('registros_removidos')}")
                        return True  # Sucesso! Encontramos um aluno que foi excluído
                    else:
                        print(f"❌ Falha na exclusão: {result.get('message')}")
                except json.JSONDecodeError:
                    print("❌ Resposta não é JSON válido")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
        
        print("\n⚠️ Nenhum dos IDs testados resultou em exclusão bem-sucedida")
        print("Isso pode indicar que não há alunos com esses IDs ou há outro problema")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_exclusao_final()
    if sucesso:
        print("\n🎉 TESTE DE EXCLUSÃO PASSOU!")
        print("✅ A funcionalidade de exclusão está funcionando corretamente")
    else:
        print("\n⚠️ TESTE DE EXCLUSÃO NÃO PASSOU")
        print("❌ Pode haver problemas com a funcionalidade ou não há alunos para testar")