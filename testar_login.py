#!/usr/bin/env python3
"""
Script para testar o login diretamente
"""
import hashlib

def testar_credenciais():
    """Testa as credenciais de login"""
    print("🔐 Testando credenciais de login...")
    
    # Credenciais de teste
    usuario = 'admin'
    senha = 'admin123'
    
    # Hash da senha
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    print(f"Usuário: {usuario}")
    print(f"Senha: {senha}")
    print(f"Hash da senha: {senha_hash}")
    
    # Dados dos usuários do sistema
    USUARIOS = {
        'admin': {
            'senha': hashlib.sha256('admin123'.encode()).hexdigest(),
            'nome': 'Administrador Geral',
            'nivel': 'admin',
            'permissoes': ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'],
            'ativo': True,
            'data_criacao': '02/01/2024',
            'criado_por': 'admin_master'
        }
    }
    
    # Verificar se o usuário existe
    if usuario in USUARIOS:
        print(f"✅ Usuário '{usuario}' encontrado!")
        
        # Verificar se a senha está correta
        if USUARIOS[usuario]['senha'] == senha_hash:
            print(f"✅ Senha correta!")
            print(f"   Nome: {USUARIOS[usuario]['nome']}")
            print(f"   Nível: {USUARIOS[usuario]['nivel']}")
            print(f"   Ativo: {USUARIOS[usuario]['ativo']}")
        else:
            print(f"❌ Senha incorreta!")
            print(f"   Hash esperado: {USUARIOS[usuario]['senha']}")
            print(f"   Hash fornecido: {senha_hash}")
    else:
        print(f"❌ Usuário '{usuario}' não encontrado!")
        print(f"Usuários disponíveis: {list(USUARIOS.keys())}")

if __name__ == "__main__":
    testar_credenciais()
