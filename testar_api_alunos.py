#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar especificamente a API de alunos
"""

import requests
import json
from datetime import datetime

print("🧪 TESTE DA API DE ALUNOS")
print("="*50)

BASE_URL = "http://localhost:5000"

def testar_api_buscar_alunos():
    """Testa a API de buscar alunos"""
    try:
        print(f"\n🔍 Testando API /buscar_alunos...")
        response = requests.get(f"{BASE_URL}/buscar_alunos", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    total_alunos = len(data)
                    print(f"   ✅ API funcionando - {total_alunos} alunos encontrados")
                    
                    if total_alunos == 315:
                        print("   🎉 PERFEITO! Exatamente 315 alunos como esperado")
                    elif total_alunos > 0:
                        print(f"   ⚠️  Encontrados {total_alunos} alunos (esperado: 315)")
                    else:
                        print("   ❌ Nenhum aluno encontrado")
                    
                    # Mostrar alguns exemplos
                    if total_alunos > 0:
                        print(f"\n📋 Primeiros 3 alunos:")
                        for i, aluno in enumerate(data[:3]):
                            nome = aluno.get('nome', 'Nome não encontrado')
                            turma = aluno.get('turma', 'Turma não definida')
                            print(f"   {i+1}. {nome} - Turma: {turma}")
                    
                    return total_alunos
                else:
                    print(f"   ❌ Resposta não é uma lista: {type(data)}")
                    print(f"   Conteúdo: {data}")
            except json.JSONDecodeError:
                print(f"   ❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:200]}...")
        else:
            print(f"   ❌ API retornou erro {response.status_code}")
            print(f"   Conteúdo: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar API: {e}")
    
    return 0

def testar_pagina_alunos():
    """Testa a página de alunos"""
    try:
        print(f"\n🔍 Testando página /alunos...")
        response = requests.get(f"{BASE_URL}/alunos", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "Alunos Cadastrados" in content or "alunos" in content.lower():
                print("   ✅ Página de alunos carregou")
                
                # Verificar se há indicação de quantidade
                if "315" in content:
                    print("   🎉 Número 315 encontrado na página!")
                elif any(num in content for num in ["300", "310", "320"]):
                    print("   ⚠️  Número próximo a 315 encontrado")
                else:
                    print("   ⚠️  Número 315 não encontrado na página")
            else:
                print("   ❌ Página não parece ser de alunos")
        else:
            print(f"   ❌ Página retornou erro {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar página: {e}")

def main():
    print(f"⏰ Teste iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar se aplicação está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Aplicação não está rodando")
            return
    except:
        print("❌ Aplicação não está rodando")
        return
    
    print("✅ Aplicação está rodando")
    
    # Testar API
    total_alunos = testar_api_buscar_alunos()
    
    # Testar página
    testar_pagina_alunos()
    
    print("\n" + "="*50)
    print("📊 RESUMO:")
    if total_alunos == 315:
        print("✅ SUCESSO: 315 alunos encontrados na API")
        print("✅ A aplicação local está funcionando corretamente")
    elif total_alunos > 0:
        print(f"⚠️  PARCIAL: {total_alunos} alunos encontrados (esperado: 315)")
        print("⚠️  Pode haver problema no carregamento dos dados")
    else:
        print("❌ FALHA: Nenhum aluno encontrado")
        print("❌ Há problema no carregamento dos dados")
    print("="*50)
    
if __name__ == "__main__":
    main()