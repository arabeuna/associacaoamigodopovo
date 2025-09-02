#!/usr/bin/env python3
"""
Teste Direto de Debug - Identifica problema específico
"""

import sys
import requests
import json
from datetime import datetime

def test_database_direct():
    """Teste direto com o banco de dados"""
    print("🔍 TESTE DIRETO COM BANCO DE DADOS", flush=True)
    print("="*50, flush=True)
    
    try:
        # Importar módulos do sistema
        sys.path.append('.')
        from database_integration import DatabaseIntegration
        
        # Conectar com o banco
        db_integration = DatabaseIntegration()
        
        print("✅ Conexão com banco estabelecida", flush=True)
        
        # Listar atividades
        print("\n📋 Atividades no banco:", flush=True)
        atividades = db_integration.listar_atividades_db()
        for atividade in atividades:
            print(f"  - {atividade['nome']} (ID: {atividade['id']})", flush=True)
        
        # Listar turmas
        print("\n📋 Turmas no banco:", flush=True)
        turmas = db_integration.listar_turmas_db()
        for turma in turmas:
            print(f"  - {turma['nome']} (Atividade: {turma['atividade']}, ID: {turma['id']})", flush=True)
        
        # Testar salvamento direto
        print("\n🧪 Testando salvamento direto no banco...", flush=True)
        
        # Usar primeira atividade e turma disponíveis
        if atividades and turmas:
            primeira_atividade = atividades[0]['nome']
            primeira_turma = turmas[0]['nome']
            
            dados_teste = {
                'nome': f'Teste DB Direto {datetime.now().strftime("%H%M%S")}',
                'telefone': '11666666666',
                'email': 'teste.db@direct.com',
                'endereco': 'Rua Teste DB, 789',
                'data_nascimento': '1980-12-25',
                'atividade': primeira_atividade,
                'turma': primeira_turma,
                'status_frequencia': 'Ativo',
                'observacoes': 'Teste direto no banco'
            }
            
            print(f"📤 Dados para teste: {dados_teste}", flush=True)
            
            # Tentar salvar diretamente
            aluno_id = db_integration.salvar_aluno_db(dados_teste)
            
            if aluno_id:
                print(f"✅ SUCESSO! Aluno salvo com ID: {aluno_id}", flush=True)
            else:
                print("❌ FALHA no salvamento direto", flush=True)
        else:
            print("⚠️ Não há atividades ou turmas disponíveis", flush=True)
            
        db_integration.db.close()
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}", flush=True)
        import traceback
        traceback.print_exc()

def test_with_web_request():
    """Teste via requisição web com dados corretos"""
    print("\n" + "="*50, flush=True)
    print("🌐 TESTE VIA REQUISIÇÃO WEB", flush=True)
    print("="*50, flush=True)
    
    server_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login
    print("🔐 Fazendo login...", flush=True)
    login_response = session.post(
        f"{server_url}/login",
        data={'usuario': 'admin', 'senha': 'admin123'},
        timeout=10,
        allow_redirects=False
    )
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Falha no login: {login_response.status_code}", flush=True)
        return
    
    print("✅ Login OK", flush=True)
    
    # Tentar obter atividades via página de cadastro
    print("\n🔍 Verificando página de cadastro...", flush=True)
    try:
        cadastro_response = session.get(f"{server_url}/novo_aluno", timeout=10)
        if cadastro_response.status_code == 200:
            print("✅ Página de cadastro acessível", flush=True)
            # Procurar por atividades no HTML
            if 'Futebol' in cadastro_response.text:
                print("✅ Atividade 'Futebol' encontrada na página", flush=True)
            if 'Manhã' in cadastro_response.text:
                print("✅ Turma 'Manhã' encontrada na página", flush=True)
        else:
            print(f"⚠️ Problema ao acessar página de cadastro: {cadastro_response.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao verificar página de cadastro: {e}", flush=True)
    
    # Testar cadastro com dados mínimos
    print("\n🧪 Testando cadastro via web...", flush=True)
    
    # Dados mínimos mas completos
    test_data = {
        'nome': f'Web Test {datetime.now().strftime("%H%M%S")}',
        'telefone': '11555555555',
        'email': 'web@test.com',
        'endereco': 'Rua Web Test, 321',
        'data_nascimento': '1975-06-10',
        'atividade': 'Futebol',
        'turma': 'Manhã',
        'status': 'Ativo',
        'observacoes': 'Teste via web'
    }
    
    print(f"📤 Enviando dados: {test_data}", flush=True)
    
    try:
        response = session.post(
            f"{server_url}/cadastrar_aluno",
            data=test_data,
            timeout=15
        )
        
        print(f"\n📡 Status: {response.status_code}", flush=True)
        
        try:
            result = response.json()
            print(f"📊 Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}", flush=True)
            
            if result.get('success'):
                print("\n✅ SUCESSO VIA WEB!", flush=True)
            else:
                print(f"\n❌ FALHA VIA WEB: {result.get('message')}", flush=True)
                
        except json.JSONDecodeError:
            print(f"\n⚠️ Resposta não é JSON:", flush=True)
            print(response.text[:1000], flush=True)
            
    except Exception as e:
        print(f"\n❌ Erro na requisição web: {e}", flush=True)

def test_minimal_data():
    """Teste com dados absolutamente mínimos"""
    print("\n" + "="*50, flush=True)
    print("🎯 TESTE COM DADOS MÍNIMOS", flush=True)
    print("="*50, flush=True)
    
    server_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login
    login_response = session.post(
        f"{server_url}/login",
        data={'usuario': 'admin', 'senha': 'admin123'},
        timeout=10,
        allow_redirects=False
    )
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Falha no login: {login_response.status_code}", flush=True)
        return
    
    # Dados absolutamente mínimos
    minimal_data = {
        'nome': f'Min {datetime.now().strftime("%H%M%S")}',
        'telefone': '11444444444',
        'atividade': 'Futebol',
        'turma': 'Manhã',
        'status': 'Ativo'
    }
    
    print(f"📤 Dados mínimos: {minimal_data}", flush=True)
    
    try:
        response = session.post(
            f"{server_url}/cadastrar_aluno",
            data=minimal_data,
            timeout=15
        )
        
        print(f"📡 Status: {response.status_code}", flush=True)
        
        try:
            result = response.json()
            print(f"📊 Resultado mínimo: {result}", flush=True)
        except:
            print(f"📄 Resposta bruta: {response.text[:500]}", flush=True)
            
    except Exception as e:
        print(f"❌ Erro: {e}", flush=True)

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO COMPLETO", flush=True)
    sys.stdout.flush()
    
    # Teste 1: Verificar banco diretamente
    test_database_direct()
    
    # Teste 2: Requisição web com dados completos
    test_with_web_request()
    
    # Teste 3: Dados mínimos
    test_minimal_data()
    
    print("\n🏁 DIAGNÓSTICO CONCLUÍDO", flush=True)
    sys.stdout.flush()