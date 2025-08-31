#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def testar_busca_modo_teste():
    """Testa busca na interface web usando modo de teste"""
    print("🌐 Testando interface web de busca (modo teste)...")
    
    # URL base
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Testar busca sem filtro (modo teste)
        print("🔍 Testando busca sem filtro (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?teste=true")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                print(f"✅ Busca bem-sucedida! Encontrados {dados.get('total_encontrado', 0)} alunos")
                
                # Mostrar primeiros 3 alunos
                alunos = dados.get('alunos', [])
                for i, aluno in enumerate(alunos[:3]):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                
                if len(alunos) > 3:
                    print(f"   ... e mais {len(alunos) - 3} alunos")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                print(f"   Resposta: {response.text[:500]}...")
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"   Resposta: {response.text[:500]}...")
        
        # 2. Testar busca com filtro "joão" (modo teste)
        print("\n🔍 Testando busca com filtro 'joão' (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?teste=true&termo=joão")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                print(f"✅ Busca com filtro bem-sucedida! Encontrados {dados.get('total_encontrado', 0)} alunos")
                
                # Mostrar todos os alunos encontrados
                alunos = dados.get('alunos', [])
                for i, aluno in enumerate(alunos):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON da busca filtrada: {e}")
        else:
            print(f"❌ Erro na busca com filtro: {response.status_code}")
        
        # 3. Testar busca com filtro "alexandre" (modo teste)
        print("\n🔍 Testando busca com filtro 'alexandre' (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?teste=true&termo=alexandre")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                dados = response.json()
                print(f"✅ Busca com filtro bem-sucedida! Encontrados {dados.get('total_encontrado', 0)} alunos")
                
                # Mostrar todos os alunos encontrados
                alunos = dados.get('alunos', [])
                for i, aluno in enumerate(alunos):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')} - {aluno.get('atividade', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON da busca filtrada: {e}")
        else:
            print(f"❌ Erro na busca com filtro: {response.status_code}")
        
        print("\n✅ Teste da interface web (modo teste) concluído!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    testar_busca_modo_teste()
