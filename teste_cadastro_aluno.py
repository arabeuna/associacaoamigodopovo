import requests
import json
from datetime import datetime
import uuid

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

def cadastrar_aluno(session, dados_aluno):
    """Testa o cadastro de um novo aluno"""
    print(f"\nTentando cadastrar aluno: {dados_aluno['nome']}...")
    print(f"Dados a serem enviados: {json.dumps(dados_aluno, indent=2, ensure_ascii=False)}")
    
    # Cadastrar via POST
    response = session.post(f'{BASE_URL}/cadastrar_aluno', data=dados_aluno)
    
    print(f"\nResposta do cadastro:")
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if 'application/json' in response.headers.get('Content-Type', ''):
        try:
            resultado = response.json()
            print(f"Resposta JSON: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
            
            if resultado.get('success'):
                print(f"✓ Aluno {dados_aluno['nome']} cadastrado com sucesso!")
                print(f"Mensagem: {resultado.get('message')}")
                print(f"Total de alunos: {resultado.get('total_alunos', 'N/A')}")
                return True
            else:
                print(f"✗ Falha no cadastro: {resultado.get('message')}")
                return False
        except json.JSONDecodeError:
            print("✗ Resposta não é JSON válido")
            print(f"Conteúdo da resposta: {response.text[:500]}...")
            return False
    else:
        print("✗ Resposta não é JSON")
        print(f"Conteúdo da resposta: {response.text[:500]}...")
        return False

def gerar_dados_teste():
    """Gera dados de teste para cadastro"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    id_unico = str(uuid.uuid4())[:8]
    
    return {
        'nome': f'Teste Cadastro {timestamp}',
        'telefone': f'(11) 9{id_unico[:4]}-{id_unico[4:8]}',
        'email': f'teste.cadastro.{timestamp}@email.com',
        'endereco': f'Rua Teste Cadastro, {id_unico[:3]}',
        'data_nascimento': '1995-05-15',
        'titulo_eleitor': f'{id_unico[:4]}{id_unico[4:8]}0000',
        'atividade': 'Informática',  # Usar uma atividade que sabemos que existe
        'turma': 'A definir',
        'status': 'Ativo',  # Campo obrigatório - valores válidos: Ativo, Inativo, Suspenso, Transferido
        'observacoes': f'Cadastro de teste realizado em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'
    }

def verificar_cadastro(session, nome_aluno):
    """Verifica se o aluno foi cadastrado com sucesso"""
    print(f"\nVerificando se o aluno '{nome_aluno}' foi cadastrado...")
    
    # Buscar o aluno na lista
    response = session.get(f'{BASE_URL}/buscar_alunos', params={'termo': nome_aluno})
    
    if response.status_code == 200:
        try:
            dados = response.json()
            if dados.get('success'):
                alunos = dados.get('alunos', [])
                aluno_encontrado = None
                
                for aluno in alunos:
                    if aluno.get('nome') == nome_aluno:
                        aluno_encontrado = aluno
                        break
                
                if aluno_encontrado:
                    print(f"✓ Aluno encontrado na base de dados!")
                    print(f"  ID: {aluno_encontrado.get('id')}")
                    print(f"  Nome: {aluno_encontrado.get('nome')}")
                    print(f"  Telefone: {aluno_encontrado.get('telefone')}")
                    print(f"  Atividade: {aluno_encontrado.get('atividade')}")
                    return True
                else:
                    print(f"✗ Aluno não encontrado na base de dados")
                    return False
            else:
                print(f"✗ Erro na busca: {dados.get('message')}")
                return False
        except json.JSONDecodeError:
            print("✗ Resposta da busca não é JSON válido")
            return False
    else:
        print(f"✗ Erro na busca. Status: {response.status_code}")
        return False

def main():
    print("=== TESTE DE CADASTRO DE ALUNO ===")
    print(f"URL Base: {BASE_URL}")
    print(f"Usuário: {USUARIO}")
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # 1. Fazer login
        if not fazer_login(session):
            return
        
        # 2. Gerar dados de teste
        dados_teste = gerar_dados_teste()
        
        print(f"\n=== DADOS DE TESTE GERADOS ===")
        print(f"Nome: {dados_teste['nome']}")
        print(f"Telefone: {dados_teste['telefone']}")
        print(f"Email: {dados_teste['email']}")
        print(f"Atividade: {dados_teste['atividade']}")
        
        # 3. Tentar cadastrar o aluno
        sucesso_cadastro = cadastrar_aluno(session, dados_teste)
        
        if sucesso_cadastro:
            # 4. Verificar se o cadastro foi persistido
            sucesso_verificacao = verificar_cadastro(session, dados_teste['nome'])
            
            if sucesso_verificacao:
                print("\n✓ TESTE DE CADASTRO CONCLUÍDO COM SUCESSO!")
                print("  - Aluno cadastrado com sucesso")
                print("  - Dados persistidos na base de dados")
            else:
                print("\n⚠️ CADASTRO PARCIALMENTE BEM-SUCEDIDO")
                print("  - Aluno cadastrado, mas não encontrado na busca")
        else:
            print("\n✗ TESTE DE CADASTRO FALHOU")
            
    except Exception as e:
        print(f"\n✗ Erro durante o teste: {str(e)}")
    
    finally:
        session.close()

if __name__ == '__main__':
    main()