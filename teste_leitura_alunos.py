import requests
import json

# Configurações
BASE_URL = 'http://localhost:5000'
USUARIO = 'admin'
SENHA = 'admin123'

def fazer_login(session):
    """Realiza login no sistema"""
    login_data = {
        'usuario': USUARIO,
        'senha': SENHA
    }
    
    response = session.post(f'{BASE_URL}/login', data=login_data)
    
    if response.status_code == 200 and 'dashboard' in response.url:
        print("✓ Login realizado com sucesso")
        return True
    else:
        print(f"✗ Falha no login. Status: {response.status_code}")
        return False

def testar_busca_todos_alunos(session):
    """Testa a busca de todos os alunos"""
    print("\n=== TESTE: BUSCAR TODOS OS ALUNOS ===")
    
    response = session.get(f'{BASE_URL}/buscar_alunos')
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        try:
            dados = response.json()
            if dados.get('success'):
                alunos = dados.get('alunos', [])
                total = len(alunos)
                print(f"✓ Busca realizada com sucesso!")
                print(f"  Total de alunos encontrados: {total}")
                
                if total > 0:
                    print(f"  Primeiro aluno: {alunos[0].get('nome')} (ID: {alunos[0].get('id')})")
                    if total > 1:
                        print(f"  Último aluno: {alunos[-1].get('nome')} (ID: {alunos[-1].get('id')})")
                return True, alunos
            else:
                print(f"✗ Erro na busca: {dados.get('message')}")
                return False, []
        except json.JSONDecodeError:
            print("✗ Resposta não é JSON válido")
            return False, []
    else:
        print(f"✗ Erro na requisição. Status: {response.status_code}")
        return False, []

def testar_busca_por_termo(session, termo):
    """Testa a busca de alunos por termo"""
    print(f"\n=== TESTE: BUSCAR ALUNOS POR TERMO '{termo}' ===")
    
    response = session.get(f'{BASE_URL}/buscar_alunos', params={'termo': termo})
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        try:
            dados = response.json()
            if dados.get('success'):
                alunos = dados.get('alunos', [])
                total = len(alunos)
                print(f"✓ Busca por termo realizada com sucesso!")
                print(f"  Alunos encontrados com '{termo}': {total}")
                
                for i, aluno in enumerate(alunos[:5]):  # Mostrar apenas os primeiros 5
                    print(f"  {i+1}. {aluno.get('nome')} (ID: {aluno.get('id')}) - {aluno.get('atividade')}")
                
                if total > 5:
                    print(f"  ... e mais {total - 5} alunos")
                    
                return True, alunos
            else:
                print(f"✗ Erro na busca: {dados.get('message')}")
                return False, []
        except json.JSONDecodeError:
            print("✗ Resposta não é JSON válido")
            return False, []
    else:
        print(f"✗ Erro na requisição. Status: {response.status_code}")
        return False, []

def testar_busca_por_id(session, aluno_id):
    """Testa a busca de um aluno específico por ID"""
    print(f"\n=== TESTE: BUSCAR ALUNO POR ID {aluno_id} ===")
    
    # Usar a rota de edição para obter dados de um aluno específico
    response = session.get(f'{BASE_URL}/editar_aluno/{aluno_id}')
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Se retornar HTML, significa que encontrou o aluno (página de edição)
        if 'text/html' in response.headers.get('Content-Type', ''):
            print(f"✓ Aluno com ID {aluno_id} encontrado!")
            print(f"  Página de edição carregada com sucesso")
            return True
        else:
            print(f"✗ Resposta inesperada para ID {aluno_id}")
            return False
    elif response.status_code == 404:
        print(f"✗ Aluno com ID {aluno_id} não encontrado")
        return False
    else:
        print(f"✗ Erro na requisição. Status: {response.status_code}")
        return False

def testar_busca_avancada(session):
    """Testa diferentes cenários de busca"""
    print("\n=== TESTE: CENÁRIOS DE BUSCA AVANÇADA ===")
    
    cenarios = [
        ('Informática', 'busca por atividade'),
        ('Maria', 'busca por nome comum'),
        ('João', 'busca por nome comum'),
        ('Silva', 'busca por sobrenome comum'),
        ('999999999', 'busca por termo inexistente'),
        ('', 'busca vazia (todos os alunos)')
    ]
    
    resultados = []
    
    for termo, descricao in cenarios:
        print(f"\n  Testando {descricao}...")
        sucesso, alunos = testar_busca_por_termo(session, termo)
        resultados.append({
            'termo': termo,
            'descricao': descricao,
            'sucesso': sucesso,
            'total_encontrados': len(alunos) if sucesso else 0
        })
    
    print("\n=== RESUMO DOS TESTES DE BUSCA AVANÇADA ===")
    for resultado in resultados:
        status = "✓" if resultado['sucesso'] else "✗"
        print(f"  {status} {resultado['descricao']}: {resultado['total_encontrados']} alunos")
    
    return resultados

def main():
    print("=== TESTE COMPLETO DE LEITURA/BUSCA DE ALUNOS ===")
    print(f"URL Base: {BASE_URL}")
    print(f"Usuário: {USUARIO}")
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        if not fazer_login(session):
            return
        
        # 2. Testar busca de todos os alunos
        sucesso_todos, todos_alunos = testar_busca_todos_alunos(session)
        
        if sucesso_todos and len(todos_alunos) > 0:
            # 3. Testar busca por ID usando alguns IDs existentes
            ids_para_testar = [todos_alunos[0]['id']]  # Primeiro aluno
            if len(todos_alunos) > 1:
                ids_para_testar.append(todos_alunos[-1]['id'])  # Último aluno
            if len(todos_alunos) > 10:
                ids_para_testar.append(todos_alunos[len(todos_alunos)//2]['id'])  # Aluno do meio
            
            for aluno_id in ids_para_testar:
                testar_busca_por_id(session, aluno_id)
        
        # 4. Testar busca avançada
        resultados_avancados = testar_busca_avancada(session)
        
        # 5. Resumo final
        print("\n=== RESUMO FINAL DOS TESTES DE LEITURA ===")
        
        if sucesso_todos:
            print(f"✓ Busca de todos os alunos: {len(todos_alunos)} alunos encontrados")
        else:
            print("✗ Busca de todos os alunos: FALHOU")
        
        testes_avancados_ok = sum(1 for r in resultados_avancados if r['sucesso'])
        print(f"✓ Testes de busca avançada: {testes_avancados_ok}/{len(resultados_avancados)} passaram")
        
        if sucesso_todos and testes_avancados_ok >= len(resultados_avancados) * 0.8:
            print("\n✓ FUNCIONALIDADE DE LEITURA/BUSCA FUNCIONANDO CORRETAMENTE!")
        else:
            print("\n⚠️ ALGUNS TESTES DE LEITURA FALHARAM")
            
    except Exception as e:
        print(f"\n✗ Erro durante o teste: {str(e)}")
    
    finally:
        session.close()

if __name__ == '__main__':
    main()