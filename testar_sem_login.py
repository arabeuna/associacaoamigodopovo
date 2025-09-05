#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar endpoints públicos da aplicação
"""

import requests
from datetime import datetime

print("🧪 TESTE BÁSICO DA APLICAÇÃO")
print("="*40)

BASE_URL = "http://localhost:5000"

def testar_endpoints():
    """Testa endpoints básicos"""
    endpoints = [
        ("/", "Página inicial"),
        ("/health", "Health check"),
        ("/login", "Página de login")
    ]
    
    for endpoint, desc in endpoints:
        try:
            print(f"\n🔍 Testando {desc} ({endpoint})...")
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ {desc} funcionando")
                
                # Verificar conteúdo específico
                content = response.text
                if endpoint == "/":
                    if "Associação Amigo do Povo" in content:
                        print("   ✅ Título da aplicação encontrado")
                elif endpoint == "/login":
                    if "login" in content.lower() and "password" in content.lower():
                        print("   ✅ Formulário de login encontrado")
                elif endpoint == "/health":
                    if "ok" in content.lower() or "healthy" in content.lower():
                        print("   ✅ Health check OK")
            else:
                print(f"   ❌ {desc} retornou erro {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar {desc}: {e}")

def verificar_aplicacao_rodando():
    """Verifica se a aplicação está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicação está rodando na porta 5000")
            return True
    except:
        pass
    
    print("❌ Aplicação não está rodando na porta 5000")
    print("💡 Execute 'python app.py' para iniciar a aplicação")
    return False

def main():
    print(f"⏰ Teste iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if verificar_aplicacao_rodando():
        testar_endpoints()
        
        print("\n" + "="*40)
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Abra http://localhost:5000 no navegador")
        print("2. Faça login com: admin / admin123")
        print("3. Vá para a página 'Alunos' no menu")
        print("4. Verifique se os 315 alunos aparecem")
        print("="*40)
    
if __name__ == "__main__":
    main()