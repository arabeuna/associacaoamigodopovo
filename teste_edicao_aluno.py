import requests
import json
from datetime import datetime

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

def listar_alunos(session):
    """Lista alunos para encontrar um ID válido"""
    response = session.get(f'{BASE_URL}/buscar_alunos')
    
    if response.status_code == 200:
        try:
            dados = response.json()
            if dados.get('success'):
                alunos = dados.get('alunos', [])
                print(f"✓ Encontrados {len(alunos)} alunos")
                
                # Mostrar os primeiros 5 alunos
                print("\nPrimeiros alunos encontrados:")
                for i, aluno in enumerate(alunos[:5]):
                    print(f"  ID: {aluno.get('id', 'N/A')} - Nome: {aluno.get('nome', 'N/A')}")
                
                return alunos
            else:
                print(f"✗ Erro na busca: {dados.get('message')}")
                return []
        except json.JSONDecodeError:
            print("✗ Resposta não é JSON válido")
            return []
    else:
        print(f"✗ Erro ao listar alunos. Status: {response.status_code}")
        return []

def obter_dados_aluno(session, aluno_id):
    """Obtém dados atuais do aluno via GET"""
    response = session.get(f'{BASE_URL}/editar_aluno/{aluno_id}')
    
    if response.status_code == 200:
        print(f"✓ Dados do aluno {aluno_id} obtidos com sucesso")
        return True
    else:
        print(f"✗ Erro ao obter dados do aluno {aluno_id}. Status: {response.status_code}")
        return False

def editar_aluno(session, aluno_id, dados_originais):
    """Testa a edição de um aluno"""
    # Dados para edição (modificando alguns campos)
    dados_edicao = {
        'nome': dados_originais.get('nome', 'Nome Teste'),
        'telefone': '(11) 99999-8888',  # Novo telefone
        'email': 'teste_edicao@email.com',  # Novo email
        'endereco': dados_originais.get('endereco', 'Endereço Teste'),
        'data_nascimento': '1990-01-01',
        'titulo_eleitor': '123456789012',
        'atividade': dados_originais.get('atividade', 'A definir'),
        'turma': dados_originais.get('turma', 'A definir'),
        'observacoes': f'Editado em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
    }
    
    print(f"\nTentando editar aluno {aluno_id}...")
    print(f"Dados a serem enviados: {json.dumps(dados_edicao, indent=2, ensure_ascii=False)}")
    
    # Tentar edição via POST
    response = session.post(f'{BASE_URL}/editar_aluno/{aluno_id}', data=dados_edicao)
    
    print(f"\nResposta da edição:")
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if 'application/json' in response.headers.get('Content-Type', ''):
        try:
            resultado = response.json()
            print(f"Resposta JSON: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
            
            if resultado.get('success'):
                print(f"✓ Aluno {aluno_id} editado com sucesso!")
                print(f"Mensagem: {resultado.get('message')}")
                return True
            else:
                print(f"✗ Falha na edição: {resultado.get('message')}")
                return False
        except json.JSONDecodeError:
            print("✗ Resposta não é JSON válido")
            print(f"Conteúdo da resposta: {response.text[:500]}...")
            return False
    else:
        print("✗ Resposta não é JSON")
        print(f"Conteúdo da resposta: {response.text[:500]}...")
        return False

def main():
    print("=== TESTE DE EDIÇÃO DE ALUNO ===")
    print(f"URL Base: {BASE_URL}")
    print(f"Usuário: {USUARIO}")
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        if not fazer_login(session):
            return
        
        # 2. Listar alunos para encontrar um ID válido
        alunos = listar_alunos(session)
        if not alunos:
            print("✗ Nenhum aluno encontrado para teste")
            return
        
        # 3. Selecionar o primeiro aluno para teste
        aluno_teste = alunos[0]
        aluno_id = aluno_teste.get('id')
        
        if not aluno_id:
            print("✗ ID do aluno não encontrado")
            return
        
        print(f"\n=== TESTANDO EDIÇÃO DO ALUNO ID: {aluno_id} ===")
        print(f"Nome atual: {aluno_teste.get('nome')}")
        
        # 4. Obter dados atuais do aluno
        if not obter_dados_aluno(session, aluno_id):
            return
        
        # 5. Tentar editar o aluno
        sucesso = editar_aluno(session, aluno_id, aluno_teste)
        
        if sucesso:
            print("\n✓ TESTE DE EDIÇÃO CONCLUÍDO COM SUCESSO!")
        else:
            print("\n✗ TESTE DE EDIÇÃO FALHOU")
            
    except Exception as e:
        print(f"\n✗ Erro durante o teste: {str(e)}")
    
    finally:
        session.close()

if __name__ == '__main__':
    main()