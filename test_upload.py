from app import app, get_db_integration
import tempfile
import os

def test_upload_functionality():
    """Testa se a funcionalidade de upload está funcionando"""
    print("=== TESTE DE FUNCIONALIDADE DE UPLOAD ===")
    
    # Testar se os DAOs estão funcionando
    db = get_db_integration()
    print(f"DB Integration: {type(db)}")
    print(f"Aluno DAO: {type(db.aluno_dao)}")
    
    # Contar alunos antes
    alunos_antes = db.aluno_dao.listar_todos()
    print(f"Total de alunos antes: {len(alunos_antes)}")
    
    # Testar criação de um aluno
    novo_aluno = {
        'nome': 'Teste Upload',
        'telefone': '11999999999',
        'email': 'teste@upload.com',
        'endereco': 'Rua Teste, 123',
        'observacoes': 'Aluno de teste para upload'
    }
    
    try:
        resultado = db.aluno_dao.criar(novo_aluno)
        print(f"Aluno criado com sucesso: {resultado}")
        
        # Contar alunos depois
        alunos_depois = db.aluno_dao.listar_todos()
        print(f"Total de alunos depois: {len(alunos_depois)}")
        
        if len(alunos_depois) > len(alunos_antes):
            print("✅ SUCESSO: Aluno foi criado e salvo corretamente!")
        else:
            print("❌ ERRO: Aluno não foi salvo no banco de dados")
            
    except Exception as e:
        print(f"❌ ERRO ao criar aluno: {e}")

if __name__ == "__main__":
    test_upload_functionality()