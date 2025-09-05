#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a API de alunos usando o modo de teste
"""

import requests
import json
from datetime import datetime

print("🧪 TESTE DA API DE ALUNOS (MODO TESTE)")
print("="*60)

BASE_URL = "http://localhost:5000"

def testar_api_buscar_alunos_modo_teste():
    """Testa a API de buscar alunos usando o parâmetro teste=true"""
    try:
        print(f"\n🔍 Testando API /buscar_alunos?teste=true...")
        response = requests.get(f"{BASE_URL}/buscar_alunos?teste=true", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and 'alunos' in data:
                    alunos_list = data['alunos']
                    total_alunos = len(alunos_list)
                    success = data.get('success', False)
                    
                    print(f"   ✅ API funcionando - {total_alunos} alunos encontrados")
                    
                    if total_alunos == 315:
                        print("   🎉 PERFEITO! Exatamente 315 alunos como esperado")
                    elif total_alunos > 300:
                        print(f"   ✅ MUITO BOM! {total_alunos} alunos (próximo ao esperado: 315)")
                    elif total_alunos > 0:
                        print(f"   ⚠️  Encontrados {total_alunos} alunos (esperado: 315)")
                    else:
                        print("   ❌ Nenhum aluno encontrado")
                        if 'message' in data:
                            print(f"   Erro: {data['message']}")
                        return 0
                    
                    # Mostrar alguns exemplos
                    print(f"\n📋 Primeiros 5 alunos:")
                    for i, aluno in enumerate(alunos_list[:5]):
                        nome = aluno.get('nome', 'Nome não encontrado')
                        turma = aluno.get('turma', 'Turma não definida')
                        atividade = aluno.get('atividade', 'Atividade não definida')
                        print(f"   {i+1}. {nome} - Turma: {turma} - Atividade: {atividade}")
                    
                    # Estatísticas
                    print(f"\n📊 Estatísticas:")
                    atividades = {}
                    turmas = {}
                    for aluno in alunos_list:
                        ativ = aluno.get('atividade', 'Não definida')
                        turma = aluno.get('turma', 'Não definida')
                        atividades[ativ] = atividades.get(ativ, 0) + 1
                        turmas[turma] = turmas.get(turma, 0) + 1
                    
                    print(f"   Atividades:")
                    for ativ, count in sorted(atividades.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"     - {ativ}: {count} alunos")
                    
                    print(f"   Turmas:")
                    for turma, count in sorted(turmas.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"     - {turma}: {count} alunos")
                    
                    return total_alunos
                elif isinstance(data, list):
                    total_alunos = len(data)
                    print(f"   ✅ API funcionando - {total_alunos} alunos encontrados (formato lista)")
                    return total_alunos
                else:
                    print(f"   ❌ Resposta em formato inesperado: {type(data)}")
                    if isinstance(data, dict) and 'message' in data:
                        print(f"   Erro: {data['message']}")
                    print(f"   Conteúdo: {str(data)[:200]}...")
            except json.JSONDecodeError:
                print(f"   ❌ Resposta não é JSON válido")
                print(f"   Conteúdo: {response.text[:300]}...")
        else:
            print(f"   ❌ API retornou erro {response.status_code}")
            print(f"   Conteúdo: {response.text[:300]}...")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar API: {e}")
    
    return 0

def testar_conexao_mongodb():
    """Testa se há endpoint para verificar conexão MongoDB"""
    endpoints_teste = [
        "/health",
        "/status",
        "/db_status"
    ]
    
    print(f"\n🔍 Testando endpoints de status...")
    for endpoint in endpoints_teste:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: {response.status_code}")
                content = response.text[:100]
                if "mongo" in content.lower() or "database" in content.lower():
                    print(f"      💾 Possível info de banco: {content}")
            else:
                print(f"   ❌ {endpoint}: {response.status_code}")
        except:
            print(f"   ❌ {endpoint}: Não disponível")

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
    
    # Testar conexão MongoDB
    testar_conexao_mongodb()
    
    # Testar API com modo teste
    total_alunos = testar_api_buscar_alunos_modo_teste()
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL:")
    if total_alunos == 315:
        print("🎉 SUCESSO TOTAL: 315 alunos encontrados!")
        print("✅ A aplicação local está funcionando perfeitamente")
        print("✅ Os dados estão sendo carregados corretamente do MongoDB")
    elif total_alunos > 300:
        print(f"✅ SUCESSO: {total_alunos} alunos encontrados (muito próximo ao esperado)")
        print("✅ A aplicação local está funcionando bem")
    elif total_alunos > 0:
        print(f"⚠️  PARCIAL: {total_alunos} alunos encontrados (esperado: 315)")
        print("⚠️  Pode haver problema no carregamento completo dos dados")
    else:
        print("❌ FALHA: Nenhum aluno encontrado")
        print("❌ Há problema sério no carregamento dos dados")
    print("="*60)
    
if __name__ == "__main__":
    main()