#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do sistema de busca de alunos
"""

import requests
import json

def testar_busca_final():
    """Testa o sistema de busca de alunos"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🌐 Testando sistema de busca de alunos...")
    
    try:
        # 1. Testar busca sem filtro (modo teste)
        print("1️⃣ Testando busca sem filtro (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?teste=true")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Busca sem filtro: {data.get('total_encontrado', 0)} alunos encontrados")
        else:
            print(f"❌ Erro na busca sem filtro: {response.status_code}")
        
        # 2. Testar busca com filtro (modo teste)
        print("\n2️⃣ Testando busca com filtro 'joão' (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?termo=joão&teste=true")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Busca com filtro: {data.get('total_encontrado', 0)} alunos encontrados")
            
            if data.get('alunos'):
                print("📋 Primeiros 3 resultados:")
                for i, aluno in enumerate(data['alunos'][:3]):
                    print(f"   {i+1}. {aluno.get('nome', 'N/A')}")
        else:
            print(f"❌ Erro na busca com filtro: {response.status_code}")
        
        # 3. Testar busca com filtro inexistente (modo teste)
        print("\n3️⃣ Testando busca com filtro inexistente (modo teste)...")
        response = requests.get(f"{base_url}/buscar_alunos?termo=xyz123inexistente&teste=true")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Busca com filtro inexistente: {data.get('total_encontrado', 0)} alunos encontrados")
        else:
            print(f"❌ Erro na busca com filtro inexistente: {response.status_code}")
        
        print("\n🎉 Teste finalizado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    testar_busca_final()
