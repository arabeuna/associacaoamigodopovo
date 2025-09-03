#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def listar_e_excluir_aluno():
    """Lista alunos existentes e testa exclusão com ID válido"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        print("🧪 TESTE COMPLETO: LISTAR E EXCLUIR ALUNO")
        print("=" * 50)
        
        # 1. Fazer login
        print("🔐 Fazendo login...")
        login_data = {
            'usuario': 'admin',
            'senha': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if response.status_code not in [200, 302]:
            print(f"❌ Falha no login: {response.status_code}")
            return False
        
        print("✅ Login realizado com sucesso")
        
        # 2. Listar alunos para encontrar IDs válidos
        print("\n📋 Listando alunos existentes...")
        response = session.get(f"{base_url}/buscar_alunos")
        
        if response.status_code != 200:
            print(f"❌ Erro ao listar alunos: {response.status_code}")
            return False
        
        try:
            dados = response.json()
            if dados.get('success') and dados.get('alunos'):
                alunos = dados['alunos']
                print(f"✅ Encontrados {len(alunos)} alunos")
                
                # Mostrar os primeiros 10 alunos
                print("\n📝 Primeiros alunos encontrados:")
                for i, aluno in enumerate(alunos[:10]):
                    print(f"   ID: {aluno.get('id')} - Nome: {aluno.get('nome')} - Atividade: {aluno.get('atividade')}")
                
                # Testar exclusão com o primeiro aluno
                if alunos:
                    aluno_teste = alunos[0]
                    aluno_id = aluno_teste.get('id')
                    aluno_nome = aluno_teste.get('nome')
                    
                    print(f"\n🗑️ Testando exclusão do aluno:")
                    print(f"   ID: {aluno_id}")
                    print(f"   Nome: {aluno_nome}")
                    
                    # Confirmar antes de excluir
                    print("\n⚠️ ATENÇÃO: Este teste irá EXCLUIR PERMANENTEMENTE o aluno do banco de dados!")
                    print("Pressione Enter para continuar ou Ctrl+C para cancelar...")
                    input()
                    
                    # Fazer requisição DELETE
                    response = session.delete(f"{base_url}/excluir_aluno/{aluno_id}")
                    
                    print(f"\nStatus da resposta: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if result.get('success'):
                                print(f"✅ SUCESSO! Aluno '{aluno_nome}' (ID: {aluno_id}) excluído com sucesso!")
                                print(f"   Mensagem: {result.get('message')}")
                                if result.get('frequencia_removida'):
                                    print(f"   Registros de frequência removidos: {result.get('registros_removidos')}")
                                
                                # Verificar se o aluno foi realmente removido
                                print("\n🔍 Verificando se o aluno foi removido...")
                                response = session.get(f"{base_url}/buscar_alunos")
                                if response.status_code == 200:
                                    dados_atualizados = response.json()
                                    if dados_atualizados.get('success'):
                                        novos_alunos = dados_atualizados.get('alunos', [])
                                        print(f"✅ Total de alunos após exclusão: {len(novos_alunos)}")
                                        
                                        # Verificar se o aluno específico foi removido
                                        aluno_ainda_existe = any(a.get('id') == aluno_id for a in novos_alunos)
                                        if not aluno_ainda_existe:
                                            print(f"✅ Confirmado: Aluno ID {aluno_id} foi removido da lista")
                                            return True
                                        else:
                                            print(f"❌ Erro: Aluno ID {aluno_id} ainda aparece na lista")
                                            return False
                                
                            else:
                                print(f"❌ Falha na exclusão: {result.get('message')}")
                                return False
                        except json.JSONDecodeError:
                            print("❌ Resposta não é JSON válido")
                            return False
                    else:
                        print(f"❌ Erro HTTP: {response.status_code}")
                        return False
                else:
                    print("❌ Nenhum aluno encontrado para testar")
                    return False
            else:
                print("❌ Nenhum aluno encontrado ou erro na resposta")
                return False
                
        except json.JSONDecodeError:
            print("❌ Erro ao decodificar resposta da listagem")
            return False
        
    except KeyboardInterrupt:
        print("\n⚠️ Teste cancelado pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = listar_e_excluir_aluno()
    if sucesso:
        print("\n🎉 TESTE COMPLETO PASSOU!")
        print("✅ A funcionalidade de exclusão está funcionando corretamente")
        print("✅ O aluno foi excluído com sucesso e removido da lista")
    else:
        print("\n⚠️ TESTE NÃO PASSOU")
        print("❌ Houve problemas durante o teste")