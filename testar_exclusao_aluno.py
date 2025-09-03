#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da funcionalidade de exclusão de aluno
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:5000"
USUARIO = "admin"
SENHA = "admin123"

def fazer_login(session):
    """Faz login no sistema"""
    login_data = {
        'usuario': USUARIO,
        'senha': SENHA
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Login realizado com sucesso")
        return True
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return False

def listar_alunos(session):
    """Lista os alunos para encontrar um ID válido"""
    try:
        response = session.get(f"{BASE_URL}/alunos")
        if response.status_code == 200:
            print("✅ Página de alunos acessada")
            # Aqui você pode extrair IDs dos alunos do HTML se necessário
            return True
        else:
            print(f"❌ Erro ao acessar alunos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao listar alunos: {e}")
        return False

def testar_exclusao_aluno(session, aluno_id):
    """Testa a exclusão de um aluno específico"""
    try:
        print(f"\n🗑️ Testando exclusão do aluno ID: {aluno_id}")
        
        # Fazer requisição DELETE
        response = session.delete(
            f"{BASE_URL}/excluir_aluno/{aluno_id}",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Aluno excluído com sucesso: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Falha na exclusão: {data.get('message')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Resposta não é JSON válido: {response.text[:200]}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao excluir aluno: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE EXCLUSÃO DE ALUNO")
    print("=" * 40)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    try:
        # 1. Fazer login
        if not fazer_login(session):
            return
        
        # 2. Listar alunos
        if not listar_alunos(session):
            return
        
        # 3. Testar exclusão com diferentes IDs
        # Você pode alterar estes IDs baseado nos alunos existentes
        ids_para_testar = [1, 2, 454, 999]  # IDs de exemplo
        
        for aluno_id in ids_para_testar:
            resultado = testar_exclusao_aluno(session, aluno_id)
            if resultado:
                print(f"✅ Teste com ID {aluno_id} passou")
                break  # Para após o primeiro sucesso
            else:
                print(f"❌ Teste com ID {aluno_id} falhou")
        
        print("\n📊 Teste de exclusão concluído")
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()